// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
// Original AtlanticOS C type-operand parser, included in ParseExpr.cpp's patch.
ExprResult Parser::ParseAtlanticLayoutExpression() {
  unsigned Operation = Tok.getKind();
  SourceLocation Loc = ConsumeToken();
  BalancedDelimiterTracker Parens(*this, tok::l_paren);
  if (Parens.expectAndConsume())
    return ExprError();
  TypeResult First = ParseTypeName();
  if (First.isInvalid()) {
    Parens.skipToEnd();
    return ExprError();
  }
  ParsedType Second;
  if (Operation == tok::kw___atlantic_layout_compatible) {
    if (ExpectAndConsume(tok::comma)) {
      Parens.skipToEnd();
      return ExprError();
    }
    TypeResult Right = ParseTypeName();
    if (Right.isInvalid()) {
      Parens.skipToEnd();
      return ExprError();
    }
    Second = Right.get();
  }
  if (Parens.consumeClose())
    return ExprError();
  return Actions.ActOnAtlanticLayout(Loc, Operation, First.get(), Second);
}
