import unittest
from subscriber import get_log_groups, build_groups_list


class TestGroupListBuilding(unittest.TestCase):
    def test_build_groups_list(self):
        all_groups = get_log_groups()
        groups = build_groups_list(all_groups, None, "/aws/rds.*", None)
        print(groups)
        assert len(groups) > 0


if __name__ == "__main__":
    unittest.main()
