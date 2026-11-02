	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 11, 0
	.globl	_main                           ; -- Begin function main
	.p2align	4
_main:                                  ; @main
Lfunc_begin0:
	.cfi_sections .debug_frame
	.cfi_startproc
; %bb.0:                                ; %entry
	;DEBUG_VALUE: main:argc <- $w0
	;DEBUG_VALUE: main:argv <- $x1
	.file	1 "./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c"
	.loc	1 122 2 prologue_end            ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:122:2
	; InlineAsm Start
	DEFINITION__define__AST_URGENT:	 .ascii "4"
	; InlineAsm End
	.loc	1 131 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:131:2
	; InlineAsm Start
	DEFINITION__define__TH_RECOVER:	 .ascii "969"
	; InlineAsm End
	.loc	1 132 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:132:2
	; InlineAsm Start
	DEFINITION__define__TH_KSTACKPTR:	 .ascii "264"
	; InlineAsm End
	.loc	1 136 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:136:2
	; InlineAsm Start
	DEFINITION__define__TH_THREAD_ID:	 .ascii "1184"
	; InlineAsm End
	.loc	1 150 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:150:2
	; InlineAsm Start
	DEFINITION__define__TH_ARM_MACHINE_FLAGS:	 .ascii "188"
	; InlineAsm End
	.loc	1 153 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:153:2
	; InlineAsm Start
	DEFINITION__define__TH_UPCB:	 .ascii "200"
	; InlineAsm End
	.loc	1 161 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:161:2
	; InlineAsm Start
	DEFINITION__define__TH_CTH_SELF:	 .ascii "248"
	; InlineAsm End
	.loc	1 162 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:162:2
	; InlineAsm Start
	DEFINITION__define__ACT_PREEMPT_CNT:	 .ascii "368"
	; InlineAsm End
	.loc	1 166 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:166:2
	; InlineAsm Start
	DEFINITION__define__ACT_CPUDATAP:	 .ascii "360"
	; InlineAsm End
	.loc	1 170 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:170:2
	; InlineAsm Start
	DEFINITION__define__ACT_DEBUGDATA:	 .ascii "240"
	; InlineAsm End
	.loc	1 171 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:171:2
	; InlineAsm Start
	DEFINITION__define__TH_IOTIER_OVERRIDE:	 .ascii "476"
	; InlineAsm End
	.loc	1 179 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:179:2
	; InlineAsm Start
	DEFINITION__define__ARM_CONTEXT_SIZE:	 .ascii "848"
	; InlineAsm End
	.loc	1 181 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:181:2
	; InlineAsm Start
	DEFINITION__define__SS_FLAVOR:	 .ascii "0"
	; InlineAsm End
	.loc	1 182 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:182:2
	; InlineAsm Start
	DEFINITION__define__ARM_SAVED_STATE64:	 .ascii "21"
	; InlineAsm End
	.loc	1 183 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:183:2
	; InlineAsm Start
	DEFINITION__define__ARM_SAVED_STATE64_COUNT:	 .ascii "72"
	; InlineAsm End
	.loc	1 185 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:185:2
	; InlineAsm Start
	DEFINITION__define__SS64_X0:	 .ascii "8"
	; InlineAsm End
	.loc	1 186 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:186:2
	; InlineAsm Start
	DEFINITION__define__SS64_X2:	 .ascii "24"
	; InlineAsm End
	.loc	1 187 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:187:2
	; InlineAsm Start
	DEFINITION__define__SS64_X4:	 .ascii "40"
	; InlineAsm End
	.loc	1 188 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:188:2
	; InlineAsm Start
	DEFINITION__define__SS64_X6:	 .ascii "56"
	; InlineAsm End
	.loc	1 189 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:189:2
	; InlineAsm Start
	DEFINITION__define__SS64_X8:	 .ascii "72"
	; InlineAsm End
	.loc	1 190 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:190:2
	; InlineAsm Start
	DEFINITION__define__SS64_X10:	 .ascii "88"
	; InlineAsm End
	.loc	1 191 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:191:2
	; InlineAsm Start
	DEFINITION__define__SS64_X12:	 .ascii "104"
	; InlineAsm End
	.loc	1 192 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:192:2
	; InlineAsm Start
	DEFINITION__define__SS64_X14:	 .ascii "120"
	; InlineAsm End
	.loc	1 193 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:193:2
	; InlineAsm Start
	DEFINITION__define__SS64_X15:	 .ascii "128"
	; InlineAsm End
	.loc	1 194 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:194:2
	; InlineAsm Start
	DEFINITION__define__SS64_X16:	 .ascii "136"
	; InlineAsm End
	.loc	1 195 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:195:2
	; InlineAsm Start
	DEFINITION__define__SS64_X18:	 .ascii "152"
	; InlineAsm End
	.loc	1 196 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:196:2
	; InlineAsm Start
	DEFINITION__define__SS64_X19:	 .ascii "160"
	; InlineAsm End
	.loc	1 197 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:197:2
	; InlineAsm Start
	DEFINITION__define__SS64_X20:	 .ascii "168"
	; InlineAsm End
	.loc	1 198 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:198:2
	; InlineAsm Start
	DEFINITION__define__SS64_X21:	 .ascii "176"
	; InlineAsm End
	.loc	1 199 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:199:2
	; InlineAsm Start
	DEFINITION__define__SS64_X22:	 .ascii "184"
	; InlineAsm End
	.loc	1 200 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:200:2
	; InlineAsm Start
	DEFINITION__define__SS64_X23:	 .ascii "192"
	; InlineAsm End
	.loc	1 201 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:201:2
	; InlineAsm Start
	DEFINITION__define__SS64_X24:	 .ascii "200"
	; InlineAsm End
	.loc	1 202 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:202:2
	; InlineAsm Start
	DEFINITION__define__SS64_X25:	 .ascii "208"
	; InlineAsm End
	.loc	1 203 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:203:2
	; InlineAsm Start
	DEFINITION__define__SS64_X26:	 .ascii "216"
	; InlineAsm End
	.loc	1 204 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:204:2
	; InlineAsm Start
	DEFINITION__define__SS64_X27:	 .ascii "224"
	; InlineAsm End
	.loc	1 205 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:205:2
	; InlineAsm Start
	DEFINITION__define__SS64_X28:	 .ascii "232"
	; InlineAsm End
	.loc	1 206 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:206:2
	; InlineAsm Start
	DEFINITION__define__SS64_FP:	 .ascii "240"
	; InlineAsm End
	.loc	1 207 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:207:2
	; InlineAsm Start
	DEFINITION__define__SS64_LR:	 .ascii "248"
	; InlineAsm End
	.loc	1 208 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:208:2
	; InlineAsm Start
	DEFINITION__define__SS64_SP:	 .ascii "256"
	; InlineAsm End
	.loc	1 209 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:209:2
	; InlineAsm Start
	DEFINITION__define__SS64_PC:	 .ascii "264"
	; InlineAsm End
	.loc	1 210 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:210:2
	; InlineAsm Start
	DEFINITION__define__SS64_CPSR:	 .ascii "272"
	; InlineAsm End
	.loc	1 211 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:211:2
	; InlineAsm Start
	DEFINITION__define__SS64_FAR:	 .ascii "280"
	; InlineAsm End
	.loc	1 212 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:212:2
	; InlineAsm Start
	DEFINITION__define__SS64_ESR:	 .ascii "288"
	; InlineAsm End
	.loc	1 217 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:217:2
	; InlineAsm Start
	DEFINITION__define__NS_FLAVOR:	 .ascii "304"
	; InlineAsm End
	.loc	1 218 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:218:2
	; InlineAsm Start
	DEFINITION__define__NS_COUNT:	 .ascii "308"
	; InlineAsm End
	.loc	1 219 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:219:2
	; InlineAsm Start
	DEFINITION__define__ARM_NEON_SAVED_STATE64:	 .ascii "23"
	; InlineAsm End
	.loc	1 220 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:220:2
	; InlineAsm Start
	DEFINITION__define__ARM_NEON_SAVED_STATE64_COUNT:	 .ascii "132"
	; InlineAsm End
	.loc	1 222 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:222:2
	; InlineAsm Start
	DEFINITION__define__NS64_D8:	 .ascii "448"
	; InlineAsm End
	.loc	1 223 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:223:2
	; InlineAsm Start
	DEFINITION__define__NS64_D9:	 .ascii "464"
	; InlineAsm End
	.loc	1 224 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:224:2
	; InlineAsm Start
	DEFINITION__define__NS64_D10:	 .ascii "480"
	; InlineAsm End
	.loc	1 225 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:225:2
	; InlineAsm Start
	DEFINITION__define__NS64_D11:	 .ascii "496"
	; InlineAsm End
	.loc	1 226 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:226:2
	; InlineAsm Start
	DEFINITION__define__NS64_D12:	 .ascii "512"
	; InlineAsm End
	.loc	1 227 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:227:2
	; InlineAsm Start
	DEFINITION__define__NS64_D13:	 .ascii "528"
	; InlineAsm End
	.loc	1 228 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:228:2
	; InlineAsm Start
	DEFINITION__define__NS64_D14:	 .ascii "544"
	; InlineAsm End
	.loc	1 229 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:229:2
	; InlineAsm Start
	DEFINITION__define__NS64_D15:	 .ascii "560"
	; InlineAsm End
	.loc	1 231 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:231:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q0:	 .ascii "320"
	; InlineAsm End
	.loc	1 232 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:232:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q2:	 .ascii "352"
	; InlineAsm End
	.loc	1 233 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:233:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q4:	 .ascii "384"
	; InlineAsm End
	.loc	1 234 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:234:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q6:	 .ascii "416"
	; InlineAsm End
	.loc	1 235 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:235:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q8:	 .ascii "448"
	; InlineAsm End
	.loc	1 236 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:236:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q10:	 .ascii "480"
	; InlineAsm End
	.loc	1 237 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:237:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q12:	 .ascii "512"
	; InlineAsm End
	.loc	1 238 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:238:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q14:	 .ascii "544"
	; InlineAsm End
	.loc	1 239 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:239:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q16:	 .ascii "576"
	; InlineAsm End
	.loc	1 240 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:240:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q18:	 .ascii "608"
	; InlineAsm End
	.loc	1 241 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:241:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q20:	 .ascii "640"
	; InlineAsm End
	.loc	1 242 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:242:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q22:	 .ascii "672"
	; InlineAsm End
	.loc	1 243 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:243:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q24:	 .ascii "704"
	; InlineAsm End
	.loc	1 244 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:244:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q26:	 .ascii "736"
	; InlineAsm End
	.loc	1 245 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:245:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q28:	 .ascii "768"
	; InlineAsm End
	.loc	1 246 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:246:2
	; InlineAsm Start
	DEFINITION__define__NS64_Q30:	 .ascii "800"
	; InlineAsm End
	.loc	1 247 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:247:2
	; InlineAsm Start
	DEFINITION__define__NS64_FPSR:	 .ascii "832"
	; InlineAsm End
	.loc	1 248 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:248:2
	; InlineAsm Start
	DEFINITION__define__NS64_FPCR:	 .ascii "836"
	; InlineAsm End
	.loc	1 250 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:250:2
	; InlineAsm Start
	DEFINITION__define__ARM_KERNEL_CONTEXT_SIZE:	 .ascii "192"
	; InlineAsm End
	.loc	1 252 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:252:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X19:	 .ascii "0"
	; InlineAsm End
	.loc	1 253 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:253:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X20:	 .ascii "8"
	; InlineAsm End
	.loc	1 254 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:254:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X21:	 .ascii "16"
	; InlineAsm End
	.loc	1 255 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:255:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X22:	 .ascii "24"
	; InlineAsm End
	.loc	1 256 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:256:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X23:	 .ascii "32"
	; InlineAsm End
	.loc	1 257 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:257:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X24:	 .ascii "40"
	; InlineAsm End
	.loc	1 258 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:258:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X25:	 .ascii "48"
	; InlineAsm End
	.loc	1 259 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:259:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X26:	 .ascii "56"
	; InlineAsm End
	.loc	1 260 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:260:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X27:	 .ascii "64"
	; InlineAsm End
	.loc	1 261 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:261:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_X28:	 .ascii "72"
	; InlineAsm End
	.loc	1 262 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:262:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_FP:	 .ascii "80"
	; InlineAsm End
	.loc	1 263 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:263:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_LR:	 .ascii "88"
	; InlineAsm End
	.loc	1 264 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:264:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_SP:	 .ascii "96"
	; InlineAsm End
	.loc	1 265 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:265:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_PC_WAS_IN_USER:	 .ascii "104"
	; InlineAsm End
	.loc	1 266 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:266:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_SSBS:	 .ascii "105"
	; InlineAsm End
	.loc	1 267 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:267:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_DIT:	 .ascii "106"
	; InlineAsm End
	.loc	1 268 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:268:2
	; InlineAsm Start
	DEFINITION__define__SS64_KERNEL_UAO:	 .ascii "107"
	; InlineAsm End
	.loc	1 270 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:270:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_D8:	 .ascii "112"
	; InlineAsm End
	.loc	1 271 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:271:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_D9:	 .ascii "120"
	; InlineAsm End
	.loc	1 272 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:272:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_D10:	 .ascii "128"
	; InlineAsm End
	.loc	1 273 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:273:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_D11:	 .ascii "136"
	; InlineAsm End
	.loc	1 274 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:274:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_D12:	 .ascii "144"
	; InlineAsm End
	.loc	1 275 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:275:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_D13:	 .ascii "152"
	; InlineAsm End
	.loc	1 276 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:276:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_D14:	 .ascii "160"
	; InlineAsm End
	.loc	1 277 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:277:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_D15:	 .ascii "168"
	; InlineAsm End
	.loc	1 279 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:279:2
	; InlineAsm Start
	DEFINITION__define__NS64_KERNEL_FPCR:	 .ascii "176"
	; InlineAsm End
	.loc	1 289 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:289:2
	; InlineAsm Start
	DEFINITION__define__PGBYTES:	 .ascii "4096"
	; InlineAsm End
	.loc	1 290 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:290:2
	; InlineAsm Start
	DEFINITION__define__PGSHIFT:	 .ascii "12"
	; InlineAsm End
	.loc	1 292 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:292:2
	; InlineAsm Start
	DEFINITION__define__VM_MIN_KERNEL_ADDRESS:	 .ascii "-137438953472"
	; InlineAsm End
	.loc	1 293 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:293:2
	; InlineAsm Start
	DEFINITION__define__KERNEL_STACK_SIZE:	 .ascii "16384"
	; InlineAsm End
	.loc	1 294 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:294:2
	; InlineAsm Start
	DEFINITION__define__ARM_TBI_USER_MASK:	 .ascii "-72057594037927936"
	; InlineAsm End
	.loc	1 296 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:296:2
	; InlineAsm Start
	DEFINITION__define__cdeSize:	 .ascii "16"
	; InlineAsm End
	.loc	1 298 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:298:2
	; InlineAsm Start
	DEFINITION__define__cdSize:	 .ascii "1296"
	; InlineAsm End
	.loc	1 300 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:300:2
	; InlineAsm Start
	DEFINITION__define__CPU_ACTIVE_THREAD:	 .ascii "48"
	; InlineAsm End
	.loc	1 301 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:301:2
	; InlineAsm Start
	DEFINITION__define__CPU_ISTACKPTR:	 .ascii "16"
	; InlineAsm End
	.loc	1 305 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:305:2
	; InlineAsm Start
	DEFINITION__define__CPU_INTSTACK_TOP:	 .ascii "24"
	; InlineAsm End
	.loc	1 306 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:306:2
	; InlineAsm Start
	DEFINITION__define__CPU_EXCEPSTACKPTR:	 .ascii "32"
	; InlineAsm End
	.loc	1 310 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:310:2
	; InlineAsm Start
	DEFINITION__define__CPU_EXCEPSTACK_TOP:	 .ascii "40"
	; InlineAsm End
	.loc	1 314 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:314:2
	; InlineAsm Start
	DEFINITION__define__CPU_NUMBER_GS:	 .ascii "0"
	; InlineAsm End
	.loc	1 315 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:315:2
	; InlineAsm Start
	DEFINITION__define__CPU_PENDING_AST:	 .ascii "76"
	; InlineAsm End
	.loc	1 316 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:316:2
	; InlineAsm Start
	DEFINITION__define__CPU_INT_STATE:	 .ascii "208"
	; InlineAsm End
	.loc	1 317 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:317:2
	; InlineAsm Start
	DEFINITION__define__CPU_USER_DEBUG:	 .ascii "360"
	; InlineAsm End
	.loc	1 318 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:318:2
	; InlineAsm Start
	DEFINITION__define__CPU_STAT_IRQ:	 .ascii "544"
	; InlineAsm End
	.loc	1 319 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:319:2
	; InlineAsm Start
	DEFINITION__define__CPU_STAT_IRQ_WAKE:	 .ascii "552"
	; InlineAsm End
	.loc	1 320 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:320:2
	; InlineAsm Start
	DEFINITION__define__CPU_RESET_HANDLER:	 .ascii "184"
	; InlineAsm End
	.loc	1 321 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:321:2
	; InlineAsm Start
	DEFINITION__define__CPU_PHYS_ID:	 .ascii "456"
	; InlineAsm End
	.loc	1 322 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:322:2
	; InlineAsm Start
	DEFINITION__define__CPU_TPIDR_EL0:	 .ascii "1280"
	; InlineAsm End
	.loc	1 331 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:331:2
	; InlineAsm Start
	DEFINITION__define__RTCLOCKDataSize:	 .ascii "72"
	; InlineAsm End
	.loc	1 333 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:333:2
	; InlineAsm Start
	DEFINITION__define__rhdSize:	 .ascii "16"
	; InlineAsm End
	.loc	1 338 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:338:2
	; InlineAsm Start
	DEFINITION__define__CPU_DATA_SIZE:	 .ascii "16"
	; InlineAsm End
	.loc	1 339 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:339:2
	; InlineAsm Start
	DEFINITION__define__CPU_DATA_ENTRIES:	 .ascii "8"
	; InlineAsm End
	.loc	1 341 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:341:2
	; InlineAsm Start
	DEFINITION__define__CPU_DATA_PADDR:	 .ascii "0"
	; InlineAsm End
	.loc	1 342 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:342:2
	; InlineAsm Start
	DEFINITION__define__CPU_DATA_VADDR:	 .ascii "8"
	; InlineAsm End
	.loc	1 344 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:344:2
	; InlineAsm Start
	DEFINITION__define__INTSTACK_SIZE:	 .ascii "16384"
	; InlineAsm End
	.loc	1 345 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:345:2
	; InlineAsm Start
	DEFINITION__define__EXCEPSTACK_SIZE:	 .ascii "16384"
	; InlineAsm End
	.loc	1 347 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:347:2
	; InlineAsm Start
	DEFINITION__define__PAGE_MAX_SHIFT:	 .ascii "14"
	; InlineAsm End
	.loc	1 348 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:348:2
	; InlineAsm Start
	DEFINITION__define__PAGE_MAX_SIZE:	 .ascii "16384"
	; InlineAsm End
	.loc	1 350 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:350:2
	; InlineAsm Start
	DEFINITION__define__BA_VIRT_BASE:	 .ascii "8"
	; InlineAsm End
	.loc	1 351 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:351:2
	; InlineAsm Start
	DEFINITION__define__BA_PHYS_BASE:	 .ascii "16"
	; InlineAsm End
	.loc	1 352 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:352:2
	; InlineAsm Start
	DEFINITION__define__BA_MEM_SIZE:	 .ascii "24"
	; InlineAsm End
	.loc	1 353 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:353:2
	; InlineAsm Start
	DEFINITION__define__BA_TOP_OF_KERNEL_DATA:	 .ascii "32"
	; InlineAsm End
	.loc	1 354 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:354:2
	; InlineAsm Start
	DEFINITION__define__BA_BOOT_FLAGS:	 .ascii "1136"
	; InlineAsm End
	.loc	1 382 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:382:2
	; InlineAsm Start
	DEFINITION__define__CPU_SYNC_ON_CSWITCH:	 .ascii "107"
	; InlineAsm End
	.loc	1 413 2                         ; ./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c:413:2
	mov	w0, wzr
Ltmp0:
	;DEBUG_VALUE: main:argc <- [DW_OP_LLVM_entry_value 1] $w0
	ret
Ltmp1:
Lfunc_end0:
	.cfi_endproc
                                        ; -- End function
	.section	__DWARF,__debug_loc,regular,debug
Lsection_debug_loc:
Ldebug_loc0:
.set Lset0, Lfunc_begin0-Lfunc_begin0
	.quad	Lset0
.set Lset1, Ltmp0-Lfunc_begin0
	.quad	Lset1
	.short	1                               ; Loc expr size
	.byte	80                              ; DW_OP_reg0
.set Lset2, Ltmp0-Lfunc_begin0
	.quad	Lset2
.set Lset3, Lfunc_end0-Lfunc_begin0
	.quad	Lset3
	.short	4                               ; Loc expr size
	.byte	163                             ; DW_OP_entry_value
	.byte	1                               ; 1
	.byte	80                              ; DW_OP_reg0
	.byte	159                             ; DW_OP_stack_value
	.quad	0
	.quad	0
	.section	__DWARF,__debug_abbrev,regular,debug
Lsection_abbrev:
	.byte	1                               ; Abbreviation Code
	.byte	17                              ; DW_TAG_compile_unit
	.byte	1                               ; DW_CHILDREN_yes
	.byte	37                              ; DW_AT_producer
	.byte	14                              ; DW_FORM_strp
	.byte	19                              ; DW_AT_language
	.byte	5                               ; DW_FORM_data2
	.byte	3                               ; DW_AT_name
	.byte	14                              ; DW_FORM_strp
	.ascii	"\202|"                         ; DW_AT_LLVM_sysroot
	.byte	14                              ; DW_FORM_strp
	.byte	16                              ; DW_AT_stmt_list
	.byte	23                              ; DW_FORM_sec_offset
	.byte	27                              ; DW_AT_comp_dir
	.byte	14                              ; DW_FORM_strp
	.ascii	"\341\177"                      ; DW_AT_APPLE_optimized
	.byte	25                              ; DW_FORM_flag_present
	.byte	17                              ; DW_AT_low_pc
	.byte	1                               ; DW_FORM_addr
	.byte	18                              ; DW_AT_high_pc
	.byte	6                               ; DW_FORM_data4
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	2                               ; Abbreviation Code
	.byte	46                              ; DW_TAG_subprogram
	.byte	1                               ; DW_CHILDREN_yes
	.byte	17                              ; DW_AT_low_pc
	.byte	1                               ; DW_FORM_addr
	.byte	18                              ; DW_AT_high_pc
	.byte	6                               ; DW_FORM_data4
	.ascii	"\347\177"                      ; DW_AT_APPLE_omit_frame_ptr
	.byte	25                              ; DW_FORM_flag_present
	.byte	64                              ; DW_AT_frame_base
	.byte	24                              ; DW_FORM_exprloc
	.byte	122                             ; DW_AT_call_all_calls
	.byte	25                              ; DW_FORM_flag_present
	.byte	3                               ; DW_AT_name
	.byte	14                              ; DW_FORM_strp
	.byte	58                              ; DW_AT_decl_file
	.byte	11                              ; DW_FORM_data1
	.byte	59                              ; DW_AT_decl_line
	.byte	11                              ; DW_FORM_data1
	.byte	39                              ; DW_AT_prototyped
	.byte	25                              ; DW_FORM_flag_present
	.byte	73                              ; DW_AT_type
	.byte	19                              ; DW_FORM_ref4
	.byte	63                              ; DW_AT_external
	.byte	25                              ; DW_FORM_flag_present
	.ascii	"\341\177"                      ; DW_AT_APPLE_optimized
	.byte	25                              ; DW_FORM_flag_present
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	3                               ; Abbreviation Code
	.byte	5                               ; DW_TAG_formal_parameter
	.byte	0                               ; DW_CHILDREN_no
	.byte	2                               ; DW_AT_location
	.byte	23                              ; DW_FORM_sec_offset
	.byte	3                               ; DW_AT_name
	.byte	14                              ; DW_FORM_strp
	.byte	58                              ; DW_AT_decl_file
	.byte	11                              ; DW_FORM_data1
	.byte	59                              ; DW_AT_decl_line
	.byte	11                              ; DW_FORM_data1
	.byte	73                              ; DW_AT_type
	.byte	19                              ; DW_FORM_ref4
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	4                               ; Abbreviation Code
	.byte	5                               ; DW_TAG_formal_parameter
	.byte	0                               ; DW_CHILDREN_no
	.byte	2                               ; DW_AT_location
	.byte	24                              ; DW_FORM_exprloc
	.byte	3                               ; DW_AT_name
	.byte	14                              ; DW_FORM_strp
	.byte	58                              ; DW_AT_decl_file
	.byte	11                              ; DW_FORM_data1
	.byte	59                              ; DW_AT_decl_line
	.byte	11                              ; DW_FORM_data1
	.byte	73                              ; DW_AT_type
	.byte	19                              ; DW_FORM_ref4
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	5                               ; Abbreviation Code
	.byte	36                              ; DW_TAG_base_type
	.byte	0                               ; DW_CHILDREN_no
	.byte	3                               ; DW_AT_name
	.byte	14                              ; DW_FORM_strp
	.byte	62                              ; DW_AT_encoding
	.byte	11                              ; DW_FORM_data1
	.byte	11                              ; DW_AT_byte_size
	.byte	11                              ; DW_FORM_data1
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	6                               ; Abbreviation Code
	.byte	15                              ; DW_TAG_pointer_type
	.byte	0                               ; DW_CHILDREN_no
	.byte	73                              ; DW_AT_type
	.byte	19                              ; DW_FORM_ref4
	.byte	0                               ; EOM(1)
	.byte	0                               ; EOM(2)
	.byte	0                               ; EOM(3)
	.section	__DWARF,__debug_info,regular,debug
Lsection_info:
Lcu_begin0:
.set Lset4, Ldebug_info_end0-Ldebug_info_start0 ; Length of Unit
	.long	Lset4
Ldebug_info_start0:
	.short	4                               ; DWARF version number
.set Lset5, Lsection_abbrev-Lsection_abbrev ; Offset Into Abbrev. Section
	.long	Lset5
	.byte	8                               ; Address Size (in bytes)
	.byte	1                               ; Abbrev [1] 0xb:0x72 DW_TAG_compile_unit
	.long	0                               ; DW_AT_producer
	.short	29                              ; DW_AT_language
	.long	21                              ; DW_AT_name
	.long	84                              ; DW_AT_LLVM_sysroot
.set Lset6, Lline_table_start0-Lsection_line ; DW_AT_stmt_list
	.long	Lset6
	.long	86                              ; DW_AT_comp_dir
                                        ; DW_AT_APPLE_optimized
	.quad	Lfunc_begin0                    ; DW_AT_low_pc
.set Lset7, Lfunc_end0-Lfunc_begin0     ; DW_AT_high_pc
	.long	Lset7
	.byte	2                               ; Abbrev [2] 0x2e:0x36 DW_TAG_subprogram
	.quad	Lfunc_begin0                    ; DW_AT_low_pc
.set Lset8, Lfunc_end0-Lfunc_begin0     ; DW_AT_high_pc
	.long	Lset8
                                        ; DW_AT_APPLE_omit_frame_ptr
	.byte	1                               ; DW_AT_frame_base
	.byte	111
                                        ; DW_AT_call_all_calls
	.long	88                              ; DW_AT_name
	.byte	1                               ; DW_AT_decl_file
	.byte	119                             ; DW_AT_decl_line
                                        ; DW_AT_prototyped
	.long	100                             ; DW_AT_type
                                        ; DW_AT_external
                                        ; DW_AT_APPLE_optimized
	.byte	3                               ; Abbrev [3] 0x47:0xf DW_TAG_formal_parameter
.set Lset9, Ldebug_loc0-Lsection_debug_loc ; DW_AT_location
	.long	Lset9
	.long	97                              ; DW_AT_name
	.byte	1                               ; DW_AT_decl_file
	.byte	119                             ; DW_AT_decl_line
	.long	100                             ; DW_AT_type
	.byte	4                               ; Abbrev [4] 0x56:0xd DW_TAG_formal_parameter
	.byte	1                               ; DW_AT_location
	.byte	81
	.long	102                             ; DW_AT_name
	.byte	1                               ; DW_AT_decl_file
	.byte	120                             ; DW_AT_decl_line
	.long	107                             ; DW_AT_type
	.byte	0                               ; End Of Children Mark
	.byte	5                               ; Abbrev [5] 0x64:0x7 DW_TAG_base_type
	.long	93                              ; DW_AT_name
	.byte	5                               ; DW_AT_encoding
	.byte	4                               ; DW_AT_byte_size
	.byte	6                               ; Abbrev [6] 0x6b:0x5 DW_TAG_pointer_type
	.long	112                             ; DW_AT_type
	.byte	6                               ; Abbrev [6] 0x70:0x5 DW_TAG_pointer_type
	.long	117                             ; DW_AT_type
	.byte	5                               ; Abbrev [5] 0x75:0x7 DW_TAG_base_type
	.long	107                             ; DW_AT_name
	.byte	6                               ; DW_AT_encoding
	.byte	1                               ; DW_AT_byte_size
	.byte	0                               ; End Of Children Mark
Ldebug_info_end0:
	.section	__DWARF,__debug_str,regular,debug
Linfo_string:
	.asciz	"clang version 19.1.7"          ; string offset=0
	.asciz	"./work/xnu-lab-sources/5647a1f4c6efdb54/osfmk/arm64/genassym.c" ; string offset=21
	.asciz	"/"                             ; string offset=84
	.asciz	"."                             ; string offset=86
	.asciz	"main"                          ; string offset=88
	.asciz	"int"                           ; string offset=93
	.asciz	"argc"                          ; string offset=97
	.asciz	"argv"                          ; string offset=102
	.asciz	"char"                          ; string offset=107
	.section	__DWARF,__apple_names,regular,debug
Lnames_begin:
	.long	1212240712                      ; Header Magic
	.short	1                               ; Header Version
	.short	0                               ; Header Hash Function
	.long	1                               ; Header Bucket Count
	.long	1                               ; Header Hash Count
	.long	12                              ; Header Data Length
	.long	0                               ; HeaderData Die Offset Base
	.long	1                               ; HeaderData Atom Count
	.short	1                               ; DW_ATOM_die_offset
	.short	6                               ; DW_FORM_data4
	.long	0                               ; Bucket 0
	.long	2090499946                      ; Hash in Bucket 0
.set Lset10, LNames0-Lnames_begin       ; Offset in Bucket 0
	.long	Lset10
LNames0:
	.long	88                              ; main
	.long	1                               ; Num DIEs
	.long	46
	.long	0
	.section	__DWARF,__apple_objc,regular,debug
Lobjc_begin:
	.long	1212240712                      ; Header Magic
	.short	1                               ; Header Version
	.short	0                               ; Header Hash Function
	.long	1                               ; Header Bucket Count
	.long	0                               ; Header Hash Count
	.long	12                              ; Header Data Length
	.long	0                               ; HeaderData Die Offset Base
	.long	1                               ; HeaderData Atom Count
	.short	1                               ; DW_ATOM_die_offset
	.short	6                               ; DW_FORM_data4
	.long	-1                              ; Bucket 0
	.section	__DWARF,__apple_namespac,regular,debug
Lnamespac_begin:
	.long	1212240712                      ; Header Magic
	.short	1                               ; Header Version
	.short	0                               ; Header Hash Function
	.long	1                               ; Header Bucket Count
	.long	0                               ; Header Hash Count
	.long	12                              ; Header Data Length
	.long	0                               ; HeaderData Die Offset Base
	.long	1                               ; HeaderData Atom Count
	.short	1                               ; DW_ATOM_die_offset
	.short	6                               ; DW_FORM_data4
	.long	-1                              ; Bucket 0
	.section	__DWARF,__apple_types,regular,debug
Ltypes_begin:
	.long	1212240712                      ; Header Magic
	.short	1                               ; Header Version
	.short	0                               ; Header Hash Function
	.long	2                               ; Header Bucket Count
	.long	2                               ; Header Hash Count
	.long	20                              ; Header Data Length
	.long	0                               ; HeaderData Die Offset Base
	.long	3                               ; HeaderData Atom Count
	.short	1                               ; DW_ATOM_die_offset
	.short	6                               ; DW_FORM_data4
	.short	3                               ; DW_ATOM_die_tag
	.short	5                               ; DW_FORM_data2
	.short	4                               ; DW_ATOM_type_flags
	.short	11                              ; DW_FORM_data1
	.long	0                               ; Bucket 0
	.long	1                               ; Bucket 1
	.long	193495088                       ; Hash in Bucket 0
	.long	2090147939                      ; Hash in Bucket 1
.set Lset11, Ltypes0-Ltypes_begin       ; Offset in Bucket 0
	.long	Lset11
.set Lset12, Ltypes1-Ltypes_begin       ; Offset in Bucket 1
	.long	Lset12
Ltypes0:
	.long	93                              ; int
	.long	1                               ; Num DIEs
	.long	100
	.short	36
	.byte	0
	.long	0
Ltypes1:
	.long	107                             ; char
	.long	1                               ; Num DIEs
	.long	117
	.short	36
	.byte	0
	.long	0
.subsections_via_symbols
	.section	__DWARF,__debug_line,regular,debug
Lsection_line:
Lline_table_start0:
