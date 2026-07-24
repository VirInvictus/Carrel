import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import recolor_caliblur as rc


class TestMapValue(unittest.TestCase):
    def test_maps_six_digit(self):
        new, changed = rc.map_value("background: #474747")
        self.assertTrue(changed)
        self.assertEqual(new, "background: #181616")

    def test_maps_three_digit(self):
        new, changed = rc.map_value("color: #fff")
        self.assertTrue(changed)
        self.assertEqual(new, "color: #c5c9c5")

    def test_case_insensitive(self):
        new, changed = rc.map_value("color: #F9BE03")
        self.assertTrue(changed)
        self.assertEqual(new, "color: #b6927b")

    def test_unmapped_untouched(self):
        new, changed = rc.map_value("color: #123456")
        self.assertFalse(changed)
        self.assertEqual(new, "color: #123456")

    def test_multiple_hexes_in_gradient(self):
        new, changed = rc.map_value("linear-gradient(#fff, rgba(0,0,0,.5), #323232)")
        self.assertTrue(changed)
        self.assertIn("#c5c9c5", new)
        self.assertIn("#1d1c19", new)

    def test_eight_digit_hex_not_partially_mapped(self):
        # #fff... longer hexes must not be chewed up by the 3-digit key
        new, changed = rc.map_value("color: #fffafa80")
        self.assertFalse(changed)
        self.assertEqual(new, "color: #fffafa80")


class TestMapRgba(unittest.TestCase):
    def test_maps_rgba_preserving_alpha(self):
        # rgb(50,50,50) is #323232, the cover-placeholder gradient grey
        new, changed = rc.map_value("background: rgba(50, 50, 50, .5)")
        self.assertTrue(changed)
        self.assertEqual(new, "background: rgba(29, 28, 25, .5)")

    def test_maps_rgb_without_alpha(self):
        new, changed = rc.map_value("color: rgb(255, 255, 255)")
        self.assertTrue(changed)
        self.assertEqual(new, "color: rgb(197, 201, 197)")

    def test_alert_danger_orange_becomes_dragon_red(self):
        new, changed = rc.map_value("background-color: rgba(255, 85, 51, .3)")
        self.assertTrue(changed)
        self.assertEqual(new, "background-color: rgba(196, 116, 110, .3)")

    def test_pure_black_shadow_untouched(self):
        # every rgba(0,0,0,x) in caliBlur is a drop shadow; black is correct
        new, changed = rc.map_value("box-shadow: 0 0 4px rgba(0, 0, 0, .15)")
        self.assertFalse(changed)
        self.assertEqual(new, "box-shadow: 0 0 4px rgba(0, 0, 0, .15)")

    def test_unmapped_rgb_untouched(self):
        new, changed = rc.map_value("color: rgba(1, 2, 3, .5)")
        self.assertFalse(changed)
        self.assertEqual(new, "color: rgba(1, 2, 3, .5)")

    def test_out_of_range_channel_untouched(self):
        new, changed = rc.map_value("color: rgb(999, 0, 0)")
        self.assertFalse(changed)

    def test_hex_and_rgba_in_one_gradient(self):
        new, changed = rc.map_value(
            "background: radial-gradient(rgba(50, 50, 50, .5) 50%, #1d1c19 100%)"
        )
        self.assertTrue(changed)
        self.assertIn("rgba(29, 28, 25, .5)", new)

    def test_hsla_left_alone(self):
        # caliBlur uses hsla for a few translucent whites; out of scope here
        new, changed = rc.map_value("background: hsla(0, 0%, 100%, .02)")
        self.assertFalse(changed)


class TestParseRules(unittest.TestCase):
    def test_plain_rule(self):
        rules = list(rc.parse_rules("a { color: #fff; }"))
        self.assertEqual(rules, [(None, "a", " color: #fff; ")])

    def test_media_context_tracked(self):
        css = "@media (max-width: 600px) { a { color: #fff; } } b { color: #eee; }"
        rules = list(rc.parse_rules(css))
        self.assertEqual(rules[0][0], "@media (max-width: 600px)")
        self.assertEqual(rules[0][1], "a")
        # after the media block closes, context resets
        self.assertEqual(rules[1], (None, "b", " color: #eee; "))

    def test_font_face_skipped(self):
        css = "@font-face { src: url(x.woff); } a { color: #fff; }"
        rules = list(rc.parse_rules(css))
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0][1], "a")

    def test_keyframes_yielded_whole(self):
        css = "@keyframes spin { 0% { color: #fff; } 100% { color: #999; } }"
        rules = list(rc.parse_rules(css))
        self.assertEqual(rules[0][0], "@keyframes")
        self.assertEqual(rules[0][1], "@keyframes spin")
        self.assertIn("100%", rules[0][2])

    def test_comments_stripped(self):
        rules = list(rc.parse_rules("/* x { } */ a { color: #fff; }"))
        self.assertEqual(len(rules), 1)


class TestRecolorRule(unittest.TestCase):
    def test_important_preserved(self):
        decls = rc.recolor_rule("a", "color: #fff !important")
        self.assertEqual(decls, ["    color: #c5c9c5 !important;"])

    def test_root_skipped(self):
        self.assertIsNone(rc.recolor_rule(":root", "--color-primary: #F9BE03"))

    def test_rule_without_mapped_colors_dropped(self):
        self.assertIsNone(rc.recolor_rule("a", "margin: 0; color: #123456"))

    def test_only_changed_declarations_emitted(self):
        decls = rc.recolor_rule("a", "margin: 0; color: #fff")
        self.assertEqual(decls, ["    color: #c5c9c5;"])


class TestGenerate(unittest.TestCase):
    def test_media_block_reassembled(self):
        import tempfile

        css = "@media (min-width: 768px) { .x { background: #474747; } }"
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "in.css"
            src.write_text(css, encoding="utf-8")
            out = rc.generate([src])
        self.assertIn("@media (min-width: 768px) {", out)
        self.assertIn("#181616", out)


if __name__ == "__main__":
    unittest.main()
