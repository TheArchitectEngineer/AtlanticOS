// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
// Original AtlanticOS compiler extension, not an Apple builtin implementation.
// The API emits the documented low-bit layout model needed by the C-only port.
#include "clang/AST/ASTContext.h"
#include "clang/AST/Decl.h"
#include "clang/AST/DeclCXX.h"
#include "clang/AST/Expr.h"
#include "clang/AST/RecordLayout.h"
#include "clang/Basic/TargetInfo.h"
#include "clang/Basic/TokenKinds.h"
#include "clang/Sema/Sema.h"
#include "llvm/ADT/SmallVector.h"
#include <string>

using namespace clang;

namespace {
class AtlanticLayout {
  ASTContext &Context;
  uint64_t TotalBits = 0;
  llvm::SmallVector<uint8_t, 64> Granules;
  std::string Failure;

  bool fail(llvm::StringRef Reason) {
    Failure = Reason.str();
    return false;
  }

  bool mark(uint64_t Offset, uint64_t Width, uint8_t Kind) {
    if (Offset > TotalBits || Width > TotalBits - Offset)
      return fail("field exceeds its target object representation");
    if (Width == 0)
      return true;
    for (uint64_t I = Offset / 64; I <= (Offset + Width - 1) / 64; ++I)
      Granules[I] |= Kind;
    return true;
  }

  bool visit(QualType Type, uint64_t Offset, unsigned Depth) {
    if (Depth > 128)
      return fail("type nesting exceeds the supported limit");
    Type = Context.getCanonicalType(Type);
    if (Type.getQualifiers().hasPointerAuth())
      return fail("authenticated pointer qualifiers are unsupported");
    if (Type->isDependentType() || Type->isVariablyModifiedType() ||
        Type->isIncompleteType() || Type->isSizelessType() ||
        Type->isFunctionType() || Type->isVoidType())
      return fail("requires a complete, fixed-size object type");
    uint64_t Width = Context.getTypeSize(Type);
    if (Offset > TotalBits || Width > TotalBits - Offset)
      return fail("nested object exceeds its target representation");
    if (Type->isPointerType() || Type->isBlockPointerType() ||
        Type->isNullPtrType())
      return mark(Offset, Width, 1);
    if (const auto *Atomic = Type->getAs<AtomicType>())
      return visit(Atomic->getValueType(), Offset, Depth + 1);
    if (const auto *Array = Context.getAsConstantArrayType(Type)) {
      if (Array->getSize().getActiveBits() > 64)
        return fail("array bound exceeds the supported range");
      QualType Element = Array->getElementType();
      uint64_t ElementBits = Context.getTypeSize(Element);
      if (ElementBits == 0)
        return true;
      uint64_t Count = Array->getSize().getZExtValue();
      if (Count > Width / ElementBits)
        return fail("array bound disagrees with target layout");
      for (uint64_t I = 0; I < Count; ++I)
        if (!visit(Element, Offset + I * ElementBits, Depth + 1))
          return false;
      return true;
    }
    if (const auto *Record = Type->getAs<RecordType>()) {
      const RecordDecl *Decl = Record->getDecl()->getDefinition();
      if (!Decl || isa<CXXRecordDecl>(Decl))
        return fail("only complete C records are supported");
      const ASTRecordLayout &Layout = Context.getASTRecordLayout(Decl);
      const FieldDecl *Last = nullptr;
      for (const FieldDecl *Field : Decl->fields())
        Last = Field;
      unsigned Index = 0;
      for (const FieldDecl *Field : Decl->fields()) {
        uint64_t FieldOffset = Offset + Layout.getFieldOffset(Index++);
        if (Field->isBitField()) {
          if (!mark(FieldOffset, Field->getBitWidthValue(Context), 2))
            return false;
        } else if (Field == Last && Decl->hasFlexibleArrayMember() &&
                   Field->getType()->isIncompleteArrayType()) {
          // A flexible member contributes no storage to sizeof(header).
          continue;
        } else if (!visit(Field->getType(), FieldOffset, Depth + 1)) {
          return false;
        }
      }
      return true;
    }
    if (const auto *Vector = Type->getAs<VectorType>()) {
      if (Vector->getElementType()->isBooleanType())
        return fail("packed boolean vector layout is unsupported");
      uint64_t ElementBits = Context.getTypeSize(Vector->getElementType());
      if (Vector->getNumElements() > Width / ElementBits)
        return fail("vector elements exceed target storage");
      return mark(Offset, ElementBits * Vector->getNumElements(), 2);
    }
    if (Type->isArithmeticType() || Type->isEnumeralType())
      return mark(Offset, Width, 2);
    return fail("unsupported object representation");
  }

public:
  explicit AtlanticLayout(ASTContext &Context) : Context(Context) {}

  bool compute(QualType Type) {
    Type = Context.getCanonicalType(Type);
    if (Type->isDependentType() || Type->isVariablyModifiedType() ||
        Type->isIncompleteType() || Type->isSizelessType() ||
        Type->isFunctionType() || Type->isVoidType())
      return fail("requires a complete, fixed-size object type");
    TotalBits = Context.getTypeSize(Type);
    if (TotalBits == 0 || TotalBits > 8 * 1024 * 1024)
      return fail("object size is zero or exceeds the 1 MiB metadata limit");
    Granules.assign((TotalBits + 63) / 64, 0);
    return visit(Type, 0, 0);
  }

  llvm::StringRef error() const { return Failure; }

  uint32_t summary() const {
    uint32_t Result = 0;
    for (uint8_t Kind : Granules)
      Result |= uint32_t(1) << Kind;
    return Result;
  }

  std::string signature() const {
    std::string Result;
    Result.reserve(Granules.size());
    for (uint8_t Kind : Granules)
      Result.push_back("0123456789abcdef"[Kind]);
    return Result;
  }

  bool equivalent(const AtlanticLayout &Other) const {
    return Granules == Other.Granules;
  }
};
} // namespace

ExprResult Sema::ActOnAtlanticLayout(SourceLocation Loc, unsigned Operation,
                                    ParsedType First, ParsedType Second) {
  auto Error = [&](llvm::StringRef Message) -> ExprResult {
    unsigned ID = getDiagnostics().getCustomDiagID(
        DiagnosticsEngine::Error, "AtlanticOS layout: %0");
    Diag(Loc, ID) << Message;
    return ExprError();
  };
  const auto &Target = Context.getTargetInfo();
  if (getLangOpts().CPlusPlus || getLangOpts().ObjC ||
      !Target.getTriple().isAArch64() || Target.isBigEndian() ||
      Target.getPointerWidth(LangAS::Default) != 64 || Target.getCharWidth() != 8 ||
      Target.getTriple().getArchName() == "arm64e")
    return Error("requires C and little-endian, non-arm64e AArch64 LP64");
  QualType Left = GetTypeFromParser(First);
  if (Operation == tok::kw___atlantic_layout_compatible) {
    QualType Right = GetTypeFromParser(Second);
    if (Context.hasSameUnqualifiedType(Left, Right))
      return ActOnIntegerConstant(Loc, 1);
    // void is not a layout wildcard. XNU's pointer macro tests void==void.
    if (Left->isVoidType() || Right->isVoidType())
      return ActOnIntegerConstant(Loc, 0);
    AtlanticLayout A(Context), B(Context);
    if (!A.compute(Left))
      return Error(A.error());
    if (!B.compute(Right))
      return Error(B.error());
    return ActOnIntegerConstant(Loc, A.equivalent(B));
  }
  AtlanticLayout Layout(Context);
  if (!Layout.compute(Left))
    return Error(Layout.error());
  if (Operation == tok::kw___atlantic_layout_summary)
    return IntegerLiteral::Create(Context, llvm::APInt(32, Layout.summary()),
                                  Context.UnsignedIntTy, Loc);
  if (Operation != tok::kw___atlantic_layout_signature)
    return Error("unknown layout operation");
  std::string Text = Layout.signature();
  QualType Array = Context.getConstantArrayType(
      Context.CharTy, llvm::APInt(64, Text.size() + 1), nullptr,
      ArraySizeModifier::Normal, 0);
  return StringLiteral::Create(Context, Text, StringLiteralKind::Ordinary,
                               false, Array, Loc);
}
