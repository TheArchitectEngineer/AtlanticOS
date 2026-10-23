import unittest
from tools.xnu_selection import generated_cfiles


class SourceSelectionTests(unittest.TestCase):
    def test_native_config_source_groups(self):
        text = 'CFILES=\\\n ./mach/task_server.c \\\n $(SOURCE_DIR)/osfmk/vm/vm_user.c \\\n ./device/device_server.c\nSFILES= start.s\n'
        self.assertEqual(generated_cfiles(text), ['mach/task_server.c', 'device/device_server.c'])

    def test_generation_list_is_not_kernel_selection(self):
        text = 'COMP_FILES= ./mach/upl_user.c\nCFILES= ./mach/task_server.c\n'
        self.assertNotIn('mach/upl_user.c', generated_cfiles(text))

    def test_missing_ambiguous_or_duplicate_selection(self):
        for text in ['', 'CFILES= ./mach/a.c\nCFILES= ./mach/b.c\n',
                     'CFILES= ./mach/a.c ./mach/a.c\n', 'CFILES= $(SOURCE_DIR)/vm.c\n']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                generated_cfiles(text)

    def test_escaping_or_unexpanded_generated_path(self):
        for name in ['./mach/../vm_user.c', './mach/$(NAME).c', './device/a.c;echo']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                generated_cfiles('CFILES= '+name+'\n')
