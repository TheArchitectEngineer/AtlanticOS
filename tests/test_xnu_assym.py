import unittest
from tools.xnu_assym import parse_assym, render_assym


class XnuAssymTests(unittest.TestCase):
    def test_target_decimal_and_immediate_forms(self):
        values = parse_assym('''ignored assembler instruction
DEFINITION__define__OFFSET: .ascii "264"
  DEFINITION__define__MASK: .ascii "#-1"
DEFINITION__define__LIMIT: .ascii "$18446744073709551615"
''', required=['OFFSET'])
        self.assertEqual(values, {'OFFSET':264, 'MASK':-1, 'LIMIT':2**64-1})
        text = render_assym(values)
        self.assertIn('#define OFFSET_NUM 264\n', text)
        self.assertIn('#define LIMIT 18446744073709551615\n', text)

    def test_integrated_assembler_byte_form_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'representation'):
            parse_assym('DEFINITION__define__OFFSET:\n.byte 52')

    def test_duplicate_even_equal_is_rejected(self):
        line = 'DEFINITION__define__OFFSET: .ascii "264"\n'
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            parse_assym(line+line)

    def test_alias_collision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'alias'):
            parse_assym('DEFINITION__define__A: .ascii "1"\nDEFINITION__define__A_NUM: .ascii "2"')

    def test_missing_required_or_empty_is_rejected(self):
        for text in ['', 'mov x0, x1', 'DEFINITION__define__OTHER: .ascii "0"']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_assym(text, required=['REQUIRED'])

    def test_malformed_or_executable_values_are_rejected(self):
        for value in ['0x100', '1+2', '0"; .long 1; "', 'NaN', '', '##2']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_assym('DEFINITION__define__OFFSET: .ascii "'+value+'"')

    def test_integer_bounds_and_oversized_metadata(self):
        for value in [str(-(2**63)-1), str(2**64)]:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'range'):
                parse_assym('DEFINITION__define__OFFSET: .ascii "'+value+'"')
        with self.assertRaisesRegex(ValueError, 'oversized'):
            parse_assym(' '*((2*1024*1024)+1))

    def test_namespaced_assertions_cannot_redefine_kernel_macros(self):
        self.assertIn('#define ATL_ASSYM_PAGE_SIZE 4096\n', render_assym({'PAGE_SIZE':4096}, prefix='ATL_ASSYM_'))
        with self.assertRaises(ValueError):
            render_assym({'PAGE_SIZE':4096}, prefix='BAD\n')
