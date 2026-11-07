use jong_bangla_core::transliterate;

#[test]
fn reph_basic_spellings_match_exact_unicode() {
    check_fixture(include_str!("fixtures/reph-basic.tsv"));
}

#[test]
fn reph_conjuncts_match_exact_unicode() {
    check_fixture(include_str!("fixtures/reph-conjuncts.tsv"));
}

#[test]
fn reph_contextual_spellings_match_exact_unicode() {
    check_fixture(include_str!("fixtures/reph-contextual.tsv"));
}

#[test]
fn reph_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/reph-controls.tsv"));
}

#[test]
fn reph_respects_utf8_and_control_boundaries() {
    for (raw, base) in [("q", "ক"), ("z", "য"), ("R", "ড়"), ("Rh", "ঢ়")] {
        for boundary in ['\0', '\n', '\r', '\t', '🙂', 'ক', 'é', '\u{301}'] {
            let input = format!("rr{raw}{boundary}a{boundary}rr{raw}ry");
            let original = input.clone();
            assert_eq!(
                transliterate(&input),
                format!("র্{base}{boundary}আ{boundary}র্{base}্র্য")
            );
            assert_eq!(input, original);
        }
    }
}

#[test]
fn reph_calls_and_internal_splits_are_independent() {
    for (left, right, left_out, right_out) in [
        ("r", "rRhry", "র", "রঢ়্র্য"),
        ("rr", "Rhry", "রর", "ঢ়্র্য"),
        ("rrR", "hry", "র্ড়", "হ্র্য"),
        ("rrRh", "ry", "র্ঢ়", "র\u{200D}্য"),
        ("rrRhr", "y", "র্ঢ়্র", "ইয়"),
    ] {
        assert_eq!(transliterate(left), left_out);
        assert_eq!(transliterate(right), right_out);
    }
    assert_eq!(transliterate("rrRhry"), "র্ঢ়্র্য");
    assert_eq!(transliterate("r"), "র");
    assert_eq!(transliterate("rrr"), "র্র");
    assert_eq!(transliterate("rrr!"), "ররর!");
    assert_eq!(transliterate("rri"), "ঋ");
    assert_eq!(transliterate("a"), "আ");
}

#[test]
fn reph_handles_long_mixed_input() {
    let input = "rrqry1rrzrry2rrRrri3rrRHrr4rrShN5rrw6rrx7rrt``a8r`rrq🙂";
    let expected = "র্ক্র্য১র্যরর\u{200D}্য২র্ড়ৃ৩র্ঢ়্রর৪র্ষ্ণ৫র্্ব৬র্ক্স৭র্ৎআ৮রর্ক🙂";
    assert_eq!(transliterate(&input.repeat(1024)), expected.repeat(1024));
}

#[test]
fn four_following_r_q_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/following-r-q.tsv"));
}

#[test]
fn four_following_r_z_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/following-r-z.tsv"));
}

#[test]
fn four_following_r_retroflex_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/following-r-r-retroflex.tsv"));
}

#[test]
fn four_following_r_rh_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/following-r-rh-retroflex.tsv"));
}

#[test]
fn four_following_r_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/following-r-four-controls.tsv"));
}

#[test]
fn four_following_r_respects_utf8_and_control_boundaries() {
    for (raw, base) in [("q", "ক"), ("z", "য"), ("R", "ড়"), ("Rh", "ঢ়")] {
        for boundary in ['\0', '\n', '\r', '\t', '🙂', 'ক', 'é', '\u{301}'] {
            let input = format!("{raw}r{boundary}a{boundary}{raw}ry");
            let original = input.clone();
            assert_eq!(
                transliterate(&input),
                format!("{base}্র{boundary}আ{boundary}{base}্র্য")
            );
            assert_eq!(input, original);
        }
    }
}

#[test]
fn four_following_r_calls_and_internal_splits_are_independent() {
    for (raw, base) in [("q", "ক"), ("z", "য"), ("R", "ড়"), ("Rh", "ঢ়")] {
        assert_eq!(transliterate(raw), base);
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate(&format!("{raw}r")), format!("{base}্র"));
        assert_eq!(transliterate("y"), "ইয়");
        assert_eq!(transliterate("ry"), "র\u{200D}্য");
    }
    for (left, right, left_out, right_out) in [
        ("R", "hry", "ড়", "হ্র্য"),
        ("Rh", "ry", "ঢ়", "র\u{200D}্য"),
        ("Rhr", "y", "ঢ়্র", "ইয়"),
    ] {
        assert_eq!(transliterate(left), left_out);
        assert_eq!(transliterate(right), right_out);
    }
    assert_eq!(transliterate("Rhry"), "ঢ়্র্য");
}

#[test]
fn four_following_r_handles_long_mixed_input() {
    let input = "qry1zrry2Rrri3RHrr4Rgr5q`ry6Rhr🙂a7";
    let expected = "ক্র্য১যরর\u{200D}্য২ড়ৃ৩ঢ়্রর৪ড়্গ্র৫কর\u{200D}্য৬ঢ়্র🙂আ৭";
    assert_eq!(transliterate(&input.repeat(1024)), expected.repeat(1024));
}

#[test]
fn final_escape_t_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/final-escape-t.tsv"));
}

#[test]
fn final_escape_consumption_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/final-escape-consumption.tsv"));
}

#[test]
fn final_escape_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/final-escape-controls.tsv"));
}

#[test]
fn final_escape_splits_and_calls_do_not_share_state() {
    for (left, right) in [("t", "``"), ("t`", "`")] {
        assert_eq!(transliterate(left), "ত");
        assert_eq!(transliterate(right), "");
    }
    assert_eq!(transliterate("t``"), "ৎ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("y"), "ইয়");
    assert_eq!(transliterate("rri"), "ঋ");
    assert_eq!(transliterate("t"), "ত");
}

#[test]
fn final_escape_resets_context_at_utf8_and_control_boundaries() {
    for boundary in ['\0', '\n', '\r', '\t', '🙂', 'ক', 'é', '\u{301}'] {
        let input = format!("kit``{boundary}a{boundary}q{boundary}t``ry");
        let original = input.clone();
        assert_eq!(
            transliterate(&input),
            format!("কিৎ{boundary}আ{boundary}ক{boundary}ৎর\u{200D}্য")
        );
        assert_eq!(input, original);
    }
}

#[test]
fn final_escape_handles_long_repeated_mixed_input() {
    let segment = "t``a1nt``a2ttt``y3t``rri`4t``o`a5T``a6t```ry7ktt``x8A`t``a9t``...0";
    let expected = "ৎআ১ন্তআ২ত্তৎইয়৩ৎৃ৪ৎআ৫টআ৬ৎর\u{200D}্য৭ক্তৎএক্স৮াৎআ৯ৎ...০";
    assert_eq!(transliterate(&segment.repeat(1024)), expected.repeat(1024));
}

#[test]
fn vowel_escapes_keep_internal_splits_and_calls_distinct() {
    for (raw, parts) in [
        ("a`", &[("আ", "")][..]),
        ("i`", &[("ই", "")][..]),
        ("I`", &[("ঈ", "")][..]),
        ("u`", &[("উ", "")][..]),
        ("U`", &[("ঊ", "")][..]),
        ("e`", &[("এ", "")][..]),
        ("ee`", &[("এ", "ে"), ("ঈ", "")][..]),
        ("o`", &[("অ", "")][..]),
        ("O`", &[("ও", "")][..]),
        ("oo`", &[("অ", ""), ("উ", "")][..]),
        ("OI`", &[("ও", "ী"), ("ঐ", "")][..]),
        ("OU`", &[("ও", "ূ"), ("ঔ", "")][..]),
        ("rri`", &[("র", "রি"), ("রর", "ি"), ("ঋ", "")][..]),
        ("A`", &[("আ", "")][..]),
        ("E`", &[("এ", "")][..]),
        ("eE`", &[("এ", "ে"), ("ঈ", "")][..]),
        ("Ee`", &[("এ", "ে"), ("ঈ", "")][..]),
        ("EE`", &[("এ", "ে"), ("ঈ", "")][..]),
    ] {
        for (split, (left, right)) in parts.iter().enumerate() {
            let split = split + 1;
            assert_eq!(transliterate(&raw[..split]), *left);
            assert_eq!(transliterate(&raw[split..]), *right);
        }
    }
    assert_eq!(transliterate("o`"), "");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("y"), "ইয়");
    assert_eq!(transliterate("k"), "ক");
    assert_eq!(transliterate("i"), "ই");
}

#[test]
fn vowel_escapes_reset_context_at_utf8_and_control_boundaries() {
    for (raw, sign) in [
        ("a`", "া"),
        ("i`", "ি"),
        ("I`", "ী"),
        ("u`", "ু"),
        ("U`", "ূ"),
        ("e`", "ে"),
        ("ee`", "ী"),
        ("o`", ""),
        ("O`", "ো"),
        ("oo`", "ু"),
        ("OI`", "ৈ"),
        ("OU`", "ৌ"),
        ("rri`", "ৃ"),
        ("A`", "া"),
        ("E`", "ে"),
        ("eE`", "ী"),
        ("Ee`", "ী"),
        ("EE`", "ী"),
    ] {
        for boundary in ['\0', '\n', '\r', '\t', '🙂', 'ক', 'é', '\u{301}'] {
            let input = format!("k{raw}{boundary}a{boundary}k{boundary}{raw}ry");
            let original = input.clone();
            assert_eq!(
                transliterate(&input),
                format!("ক{sign}{boundary}আ{boundary}ক{boundary}{sign}র\u{200D}্য")
            );
            assert_eq!(input, original);
        }
    }
}

#[test]
fn vowel_escapes_handle_long_repeated_mixed_input() {
    let segment = "ka`a1ki`y2kI`x3ku`r4kU`rr5ke`ry6kee`Z7ko`a8kO`wa9koo`kr0kOI`OI1kOU`rri2krri`a3ngee`a4ngoo`a5Ngrri`a6A`E`eE`Ee`EE`🙂";
    let expected =
        "কাআ১কিইয়২কীএক্স৩কুর৪কূরর৫কের\u{200D}্য৬কী্য৭কআ৮কোওয়া৯কুক্র০কৈঐ১কৌঋ২কৃআ৩ঙ্গেেআ৪ঙ্গআ৫ঙররিআ৬ােীীী🙂";
    assert_eq!(transliterate(&segment.repeat(1024)), expected.repeat(1024));
}

#[test]
fn vowel_escape_a_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-a.tsv"));
}

#[test]
fn vowel_escape_i_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-i.tsv"));
}

#[test]
fn vowel_escape_i_long_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-i-long.tsv"));
}

#[test]
fn vowel_escape_u_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-u.tsv"));
}

#[test]
fn vowel_escape_u_long_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-u-long.tsv"));
}

#[test]
fn vowel_escape_e_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-e.tsv"));
}

#[test]
fn vowel_escape_ee_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-ee.tsv"));
}

#[test]
fn vowel_escape_o_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-o.tsv"));
}

#[test]
fn vowel_escape_o_upper_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-o-upper.tsv"));
}

#[test]
fn vowel_escape_oo_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-oo.tsv"));
}

#[test]
fn vowel_escape_oi_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-oi.tsv"));
}

#[test]
fn vowel_escape_ou_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-ou.tsv"));
}

#[test]
fn vowel_escape_rri_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-rri.tsv"));
}

#[test]
fn vowel_escape_a_upper_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-a-upper.tsv"));
}

#[test]
fn vowel_escape_e_upper_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-e-upper.tsv"));
}

#[test]
fn vowel_escape_ee_lower_upper_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-ee-lower-upper.tsv"));
}

#[test]
fn vowel_escape_ee_upper_lower_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-ee-upper-lower.tsv"));
}

#[test]
fn vowel_escape_ee_upper_pair_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-ee-upper-pair.tsv"));
}

#[test]
fn vowel_escape_controls_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/vowel-escape-controls.tsv"));
}

#[test]
fn symbols_keep_consumed_keys_and_separate_calls_distinct() {
    for (raw, parts) in [
        ("..", &[("।", "।")][..]),
        ("...", &[("।", "।।"), ("।।", "।")][..]),
        (".`", &[("।", "")][..]),
        (":`", &[("ঃ", "")][..]),
        ("^`", &[("ঁ", "")][..]),
        (",,", &[(",", ",")][..]),
    ] {
        for (split, (left, right)) in parts.iter().enumerate() {
            let split = split + 1;
            assert_eq!(transliterate(&raw[..split]), *left);
            assert_eq!(transliterate(&raw[split..]), *right);
        }
    }
    assert_eq!(transliterate("`"), "");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("k"), "ক");
    assert_eq!(transliterate("r"), "র");
    assert_eq!(transliterate("y"), "ইয়");
}

#[test]
fn symbols_reset_context_at_utf8_and_control_boundaries() {
    for (raw, converted) in [
        (".", "।"),
        ("..", "।।"),
        ("...", "..."),
        (".`", "."),
        (":", "ঃ"),
        (":`", ":"),
        ("^", "ঁ"),
        ("^`", "^"),
        (",,", "\u{09CD}\u{200C}"),
        ("$", "৳"),
        ("`", ""),
    ] {
        for boundary in ['\0', '\n', '\r', '\t', '🙂', 'ক', 'é', '\u{301}'] {
            let input = format!("k{raw}{boundary}a{boundary}k{boundary}{raw}ry");
            let original = input.clone();
            assert_eq!(
                transliterate(&input),
                format!("ক{converted}{boundary}আ{boundary}ক{boundary}{converted}র\u{200D}্য")
            );
            assert_eq!(input, original);
        }
    }
}

#[test]
fn symbols_handle_long_repeated_mixed_input() {
    let segment = "k.`a1k..a2k...a3k:a4k^a5k,,a6k$a7k`a8r`y9G`dh0";
    let expected = "ক.আ১ক।।আ২ক...আ৩কঃআ৪কঁআ৫ক্‌আ৬ক৳আ৭কআ৮রইয়৯গধ০";
    assert_eq!(transliterate(&segment.repeat(1024)), expected.repeat(1024));
}

#[test]
fn symbols_period_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-period.tsv"));
}

#[test]
fn symbols_double_period_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-double-period.tsv"));
}

#[test]
fn symbols_ellipsis_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-ellipsis.tsv"));
}

#[test]
fn symbols_escaped_period_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-escaped-period.tsv"));
}

#[test]
fn symbols_colon_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-colon.tsv"));
}

#[test]
fn symbols_escaped_colon_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-escaped-colon.tsv"));
}

#[test]
fn symbols_caret_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-caret.tsv"));
}

#[test]
fn symbols_escaped_caret_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-escaped-caret.tsv"));
}

#[test]
fn symbols_double_comma_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-double-comma.tsv"));
}

#[test]
fn symbols_dollar_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-dollar.tsv"));
}

#[test]
fn symbols_backtick_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-backtick.tsv"));
}

#[test]
fn symbols_controls_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/symbols-controls.tsv"));
}

#[test]
fn explicit_gj_controls_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-controls.tsv"));
}

#[test]
fn explicit_gj_g_basic_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-g-basic.tsv"));
}

#[test]
fn explicit_gj_g_lower_upper_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-g-lower-upper.tsv"));
}

#[test]
fn explicit_gj_g_n_retroflex_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-g-n-retroflex.tsv"));
}

#[test]
fn explicit_gj_g_upper_lower_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-g-upper-lower.tsv"));
}

#[test]
fn explicit_gj_g_upper_pair_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-g-upper-pair.tsv"));
}

#[test]
fn explicit_gj_gdh_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-gdh.tsv"));
}

#[test]
fn explicit_gj_gh_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-gh.tsv"));
}

#[test]
fn explicit_gj_ghn_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-ghn.tsv"));
}

#[test]
fn explicit_gj_gl_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-gl.tsv"));
}

#[test]
fn explicit_gj_gm_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-gm.tsv"));
}

#[test]
fn explicit_gj_gn_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-gn.tsv"));
}

#[test]
fn explicit_gj_j_basic_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/explicit-gj-j-basic.tsv"));
}

#[test]
fn explicit_gj_resets_at_every_split_and_between_calls() {
    for (raw, parts) in [
        ("Ghn", &[("গ", "হ্ন"), ("ঘ", "ন")][..]),
        ("Gdh", &[("গ", "ধ"), ("গদ", "হ")][..]),
        ("GN", &[("গ", "ণ")][..]),
        ("Gn", &[("গ", "ন")][..]),
        ("Gm", &[("গ", "ম")][..]),
        ("Gl", &[("গ", "ল")][..]),
        ("GG", &[("গ", "গ")][..]),
        ("Gg", &[("গ", "গ")][..]),
        ("gG", &[("গ", "গ")][..]),
        ("Gh", &[("গ", "হ")][..]),
        ("Jh", &[("জ", "হ")][..]),
        ("cNG", &[("চ", "ঞ"), ("চণ", "গ")][..]),
        ("jNG", &[("জ", "ঞ"), ("জণ", "গ")][..]),
        ("ShNG", &[("শ", "হ্ণগ"), ("ষ", "ঞ"), ("ষ্ণ", "গ")][..]),
    ] {
        for (offset, (head, tail)) in parts.iter().enumerate() {
            let split = offset + 1;
            assert_eq!(transliterate(&raw[..split]), *head);
            assert_eq!(transliterate(&raw[split..]), *tail);
            for boundary in [" ", "\n", "\t", "\0", "🙂", "বাংলা", "\u{301}"] {
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{head}{boundary}{tail}"),
                );
            }
        }
    }
    let raw = String::from("G J Jh jh GN Ng NG nG ShNG Gg gG Gdh GHn cNG jNG 🙂 ");
    let expected = "গ জ জহ ঝ গ্ণ ঙ ঞ নগ ষ্ণগ জ্ঞ জ্ঞ গ্ধ ঘ্ন চ্ঞ জ্ঞ 🙂 ";
    assert_eq!(transliterate(&raw.repeat(1024)), expected.repeat(1024));
    assert_eq!(raw, "G J Jh jh GN Ng NG nG ShNG Gg gG Gdh GHn cNG jNG 🙂 ");
    assert_eq!(transliterate("G"), "গ");
    assert_eq!(transliterate("J"), "জ");
}

#[test]
fn case_alias_a_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-a.tsv"));
}

#[test]
fn case_alias_b_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-b.tsv"));
}

#[test]
fn case_alias_c_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-c.tsv"));
}

#[test]
fn case_alias_e_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-e.tsv"));
}

#[test]
fn case_alias_f_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-f.tsv"));
}

#[test]
fn case_alias_h_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-h.tsv"));
}

#[test]
fn case_alias_k_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-k.tsv"));
}

#[test]
fn case_alias_l_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-l.tsv"));
}

#[test]
fn case_alias_m_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-m.tsv"));
}

#[test]
fn case_alias_mixed_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-mixed.tsv"));
}

#[test]
fn case_alias_p_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-p.tsv"));
}

#[test]
fn case_alias_q_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-q.tsv"));
}

#[test]
fn case_alias_resolved_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-resolved.tsv"));
}

#[test]
fn case_alias_v_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-v.tsv"));
}

#[test]
fn case_alias_w_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-w.tsv"));
}

#[test]
fn case_alias_x_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/case-alias-x.tsv"));
}

const CASE_ALIAS_SPLITS: [(&str, usize, &str, &str); 25] = [
    ("CH", 1, "চ", "হ"),
    ("PH", 1, "প", "হ"),
    ("KH", 1, "ক", "হ"),
    ("SH", 1, "শ", "হ"),
    ("kSH", 1, "ক", "ষ"),
    ("kSH", 2, "কশ", "হ"),
    ("NgKH", 1, "ণ", "গখ"),
    ("NgKH", 2, "ঙ", "খ"),
    ("NgKH", 3, "ঙ্ক", "হ"),
    ("KKHN", 1, "ক", "খণ"),
    ("KKHN", 2, "ক্ক", "হ্ণ"),
    ("KKHN", 3, "ক্ষ", "ণ"),
    ("KSHM", 1, "ক", "ষ্ম"),
    ("KSHM", 2, "কশ", "হ্ম"),
    ("KSHM", 3, "ক্ষ", "ম"),
    ("AZ", 1, "আ", "্য"),
    ("EE", 1, "এ", "এ"),
    ("MPH", 1, "ম", "ফ"),
    ("MPH", 2, "ম্প", "হ"),
    ("SPL", 1, "শ", "প্ল"),
    ("SPL", 2, "শপ", "ল"),
    ("KX", 1, "ক", "এক্স"),
    ("kH", 1, "ক", "হ"),
    ("lDH", 1, "ল", "ঢ"),
    ("lDH", 2, "ল্ড", "হ"),
];

#[test]
fn case_aliases_preserve_unicode_and_reset_at_boundaries() {
    for (raw, bangla) in [
        ("A", "আ"),
        ("B", "ব"),
        ("C", "চ"),
        ("E", "এ"),
        ("F", "ফ"),
        ("H", "হ"),
        ("K", "ক"),
        ("L", "ল"),
        ("M", "ম"),
        ("P", "প"),
        ("Q", "ক"),
        ("V", "ভ"),
        ("W", "ও"),
        ("X", "এক্স"),
    ] {
        for boundary in [
            " ",
            "\n",
            "\r",
            "\t",
            "\0",
            "🙂",
            "বাংলা",
            "\u{301}",
            "K",
            "İ",
            "Ａ",
        ] {
            assert_eq!(
                transliterate(&format!("{raw}{boundary}A")),
                format!("{bangla}{boundary}আ")
            );
        }
    }
    for (raw, split, first, tail) in CASE_ALIAS_SPLITS {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "বাংলা", "\u{301}"] {
            assert_eq!(
                transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                format!("{first}{boundary}{tail}")
            );
        }
    }
    assert_eq!(transliterate("I U O T D N R S Y Z"), "ঈ ঊ ও ট ড ণ ড় শ য় ্য");
    // Explicit G/J rules retain case-sensitive matching, including separate Jh.
    assert_eq!(transliterate("G J Jh"), "গ জ জহ");
    // Preserve the existing Unicode passthrough contract, including lookalikes.
    assert_eq!(transliterate("KＫİＡÉＡ🙂K"), "KＫİＡÉＡ🙂ক");
}

#[test]
fn case_aliases_reset_between_calls_and_in_long_input() {
    for (raw, split, first, tail) in CASE_ALIAS_SPLITS {
        assert_eq!(transliterate(&raw[..split]), first);
        assert_eq!(transliterate(&raw[split..]), tail);
        assert_eq!(transliterate("A"), "আ");
    }
    let raw = "AZ KH SH NgK KSHM SPL CH PH KX WA X QX 🙂 KＡ ";
    let expected = "অ্যা খ ষ ঙ্ক ক্ষ্ম শপ্ল ছ ফ ক্ষ ওয়া এক্স কক্স 🙂 KＡ ";
    assert_eq!(transliterate(&raw.repeat(1024)), expected.repeat(1024));
}

#[test]
fn conjunct_completion_resets_at_every_split_and_between_calls() {
    for (raw, bangla, parts) in [
        ("pt", "প্ত", &[("প", "ত")][..]),
        ("pT", "প্ট", &[("প", "ট")][..]),
        ("bdh", "ব্ধ", &[("ব", "ধ"), ("ব্দ", "হ")][..]),
        ("bd", "ব্দ", &[("ব", "দ")][..]),
        ("bj", "ব্জ", &[("ব", "জ")][..]),
        ("cNG", "চ্ঞ", &[("চ", "ঞ"), ("চণ", "গ")][..]),
        ("cch", "চ্ছ", &[("চ", "ছ"), ("চ্চ", "হ")][..]),
        ("cc", "চ্চ", &[("চ", "চ")][..]),
        ("gdh", "গ্ধ", &[("গ", "ধ"), ("গদ", "হ")][..]),
        ("jjh", "জ্ঝ", &[("জ", "ঝ"), ("জ্জ", "হ")][..]),
        ("jNG", "জ্ঞ", &[("জ", "ঞ"), ("জণ", "গ")][..]),
        ("jj", "জ্জ", &[("জ", "জ")][..]),
        ("mth", "ম্থ", &[("ম", "থ"), ("মত", "হ")][..]),
        ("NGch", "ঞ্ছ", &[("ণ", "গছ"), ("ঞ", "ছ"), ("ঞ্চ", "হ")][..]),
        ("NGjh", "ঞ্ঝ", &[("ণ", "গঝ"), ("ঞ", "ঝ"), ("ঞ্জ", "হ")][..]),
        ("NGc", "ঞ্চ", &[("ণ", "গচ"), ("ঞ", "চ")][..]),
        ("NGj", "ঞ্জ", &[("ণ", "গজ"), ("ঞ", "জ")][..]),
        ("nch", "ঞ্ছ", &[("ন", "ছ"), ("ঞ্চ", "হ")][..]),
        ("njh", "ঞ্ঝ", &[("ন", "ঝ"), ("ঞ্জ", "হ")][..]),
        ("nj", "ঞ্জ", &[("ন", "জ")][..]),
        ("nc", "ঞ্চ", &[("ন", "চ")][..]),
        ("shch", "শ্ছ", &[("স", "হছ"), ("শ", "ছ"), ("শ্চ", "হ")][..]),
        ("Sch", "শ্ছ", &[("শ", "ছ"), ("শ্চ", "হ")][..]),
        ("shc", "শ্চ", &[("স", "হচ"), ("শ", "চ")][..]),
        ("Sc", "শ্চ", &[("শ", "চ")][..]),
        ("c", "চ", &[][..]),
        ("ch", "ছ", &[("চ", "হ")][..]),
        ("j", "জ", &[][..]),
        ("jh", "ঝ", &[("জ", "হ")][..]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "জ্ঞ", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                // A split exposes a fresh G; it cannot reuse the consumed N.
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(transliterate(&"pt pT bdh bd bj cNG cch cc gdh jjh jNG jj mth NGch NGjh NGc NGj nch njh nj nc shch Sch shc Sc 🙂 ".repeat(64)), "প্ত প্ট ব্ধ ব্দ ব্জ চ্ঞ চ্ছ চ্চ গ্ধ জ্ঝ জ্ঞ জ্জ ম্থ ঞ্ছ ঞ্ঝ ঞ্চ ঞ্জ ঞ্ছ ঞ্ঝ ঞ্জ ঞ্চ শ্ছ শ্ছ শ্চ শ্চ 🙂 ".repeat(64));
}

#[test]
fn conjunct_completion_consumed_and_fresh_keys_keep_their_priorities() {
    for (raw, expected) in [
        ("pt pT bd bdh bj", "প্ত প্ট ব্দ ব্ধ ব্জ"),
        ("cNG cch cc gdh jjh jNG jj mth", "চ্ঞ চ্ছ চ্চ গ্ধ জ্ঝ জ্ঞ জ্জ ম্থ"),
        ("NGch NGjh NGc NGj nch njh nj nc", "ঞ্ছ ঞ্ঝ ঞ্চ ঞ্জ ঞ্ছ ঞ্ঝ ঞ্জ ঞ্চ"),
        ("shch Sch shc Sc", "শ্ছ শ্ছ শ্চ শ্চ"),
        (
            "pthm pThm bjhm bdhm cchm jjhm mthm",
            "প্তহ্ম প্টহ্ম ব্জহ্ম ব্ধম চ্ছম জ্ঝম ম্থম",
        ),
        (
            "NGchm NGjhm nchm njhm shchm Schm",
            "ঞ্ছম ঞ্ঝম ঞ্ছম ঞ্ঝম শ্ছম শ্ছম",
        ),
        ("bdd bddh bdhn bdhhn", "ব্দদ ব্দধ ব্ধন ব্ধহ্ন"),
        ("ccNG ccc cccc ccch cNGcNG", "চ্চঞ চ্চচ চ্চচ্চ চ্চছ চ্ঞচ্ঞ"),
        ("jjNG jjj jjjj jjjh jNGjNG", "জ্জঞ জ্জজ জ্জজ্জ জ্জঝ জ্ঞজ্ঞ"),
        ("pnch pnnch snj snnj", "প্নছ প্নঞ্ছ স্নজ স্নঞ্জ"),
        (
            "ksch kshch nsch nshch psch pshch",
            "ক্সছ কশছ ন্সছ নশছ প্সছ পশছ",
        ),
        ("cr chr jr jhr cNGr jNGr", "চ্র ছ্র জ্র ঝ্র চ্ঞ্র জ্ঞ্র"),
        (
            "bjrri cchrry jNGrrZ NGchry",
            "ব্জৃ চ্ছরর\u{200d}্য জ্ঞরর\u{200d}্য ঞ্ছ্র্য",
        ),
    ] {
        assert_eq!(transliterate(raw), expected, "{raw}");
    }
}

#[test]
fn conjunct_completion_bd_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-bd.tsv"));
}

#[test]
fn conjunct_completion_bdh_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-bdh.tsv"));
}

#[test]
fn conjunct_completion_bj_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-bj.tsv"));
}

#[test]
fn conjunct_completion_c_following_r_matches_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-completion-c-following-r.tsv"
    ));
}

#[test]
fn conjunct_completion_c_nya_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-c-nya.tsv"));
}

#[test]
fn conjunct_completion_cc_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-cc.tsv"));
}

#[test]
fn conjunct_completion_cch_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-cch.tsv"));
}

#[test]
fn conjunct_completion_ch_following_r_matches_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-completion-ch-following-r.tsv"
    ));
}

#[test]
fn conjunct_completion_controls_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-controls.tsv"));
}

#[test]
fn conjunct_completion_gdh_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-gdh.tsv"));
}

#[test]
fn conjunct_completion_j_following_r_matches_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-completion-j-following-r.tsv"
    ));
}

#[test]
fn conjunct_completion_j_nya_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-j-nya.tsv"));
}

#[test]
fn conjunct_completion_jh_following_r_matches_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-completion-jh-following-r.tsv"
    ));
}

#[test]
fn conjunct_completion_jj_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-jj.tsv"));
}

#[test]
fn conjunct_completion_jjh_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-jjh.tsv"));
}

#[test]
fn conjunct_completion_mth_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-mth.tsv"));
}

#[test]
fn conjunct_completion_nc_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-nc.tsv"));
}

#[test]
fn conjunct_completion_nch_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-nch.tsv"));
}

#[test]
fn conjunct_completion_nj_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-nj.tsv"));
}

#[test]
fn conjunct_completion_njh_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-njh.tsv"));
}

#[test]
fn conjunct_completion_nya_c_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-nya-c.tsv"));
}

#[test]
fn conjunct_completion_nya_ch_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-nya-ch.tsv"));
}

#[test]
fn conjunct_completion_nya_j_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-nya-j.tsv"));
}

#[test]
fn conjunct_completion_nya_jh_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-nya-jh.tsv"));
}

#[test]
fn conjunct_completion_p_retroflex_t_matches_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-completion-p-retroflex-t.tsv"
    ));
}

#[test]
fn conjunct_completion_pt_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-pt.tsv"));
}

#[test]
fn conjunct_completion_s_uppercase_c_matches_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-completion-s-uppercase-c.tsv"
    ));
}

#[test]
fn conjunct_completion_s_uppercase_ch_matches_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-completion-s-uppercase-ch.tsv"
    ));
}

#[test]
fn conjunct_completion_sh_c_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-sh-c.tsv"));
}

#[test]
fn conjunct_completion_sh_ch_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-completion-sh-ch.tsv"));
}

#[test]
fn s_stops_sth_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sth.tsv"));
}

#[test]
fn s_stops_st_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-st.tsv"));
}

#[test]
fn s_stops_s_t_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-s-t-retroflex.tsv"));
}

#[test]
fn s_stops_sh_th_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-th-retroflex.tsv"));
}

#[test]
fn s_stops_sh_t_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-t-retroflex.tsv"));
}

#[test]
fn s_stops_sh_lowercase_t_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-lowercase-t.tsv"));
}

#[test]
fn s_stops_s_uppercase_t_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-s-uppercase-t.tsv"));
}

#[test]
fn s_stops_case_controls_and_consumed_keys_match_exact_unicode() {
    check_fixture(include_str!("fixtures/s-stop-controls.tsv"));
}

#[test]
fn s_stops_longer_exceptions_and_priorities_match() {
    for (raw, expected) in [
        ("st sth sT ShT ShTh sht St", "স্ত স্থ স্ট ষ্ট ষ্ঠ শ্ত শ্ত"),
        ("sTh shth Sth Shth", "স্টহ শ্তহ শ্তহ ষথ"),
        ("sThm shthm Sthm sthm ShThm", "স্টহ্ম শ্তহ্ম শ্তহ্ম স্থম ষ্ঠম"),
        ("stn stm stt stth sttn sttm", "স্তন স্তম স্তত স্তথ স্তত্ন স্তত্ম"),
        ("sTm ShTm ShTT ShTTh ShTTm", "স্টম ষ্টম ষ্টট ষ্টঠ ষ্টট্ম"),
        ("kst ksth ksht kSt", "ক্সত ক্সথ কশত কশ্ত"),
        (
            "nst nsth nsht nSt pst psth psht pSt",
            "ন্সত ন্সথ নশত নশ্ত প্সত প্সথ পশত পশ্ত",
        ),
        ("kShT kShTh NgkShT NgkShTh", "ক্ষট ক্ষঠ ঙ্ক্ষট ঙ্ক্ষঠ"),
        (
            "str sthr sTr ShTr ShThr shtr Str",
            "স্ত্র স্থ্র স্ট্র ষ্ট্র ষ্ঠ্র শ্ত্র শ্ত্র",
        ),
        (
            "strri sthrry sTrrZ ShThry shtrri Strry",
            "স্তৃ স্থরর\u{200d}্য স্টরর\u{200d}্য ষ্ঠ্র্য শ্তৃ শ্তরর\u{200d}্য",
        ),
    ] {
        assert_eq!(transliterate(raw), expected, "{raw}");
    }
}

#[test]
fn s_stops_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("st", "স্ত", vec![("স", "ত")]),
        ("sth", "স্থ", vec![("স", "থ"), ("স্ত", "হ")]),
        ("sT", "স্ট", vec![("স", "ট")]),
        ("ShT", "ষ্ট", vec![("শ", "হট"), ("ষ", "ট")]),
        ("ShTh", "ষ্ঠ", vec![("শ", "হঠ"), ("ষ", "ঠ"), ("ষ্ট", "হ")]),
        ("sht", "শ্ত", vec![("স", "হত"), ("শ", "ত")]),
        ("St", "শ্ত", vec![("শ", "ত")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "স্থ", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(transliterate(&"st sth sT ShT ShTh sht St sThm shthm Sthm sthm ShThm stn sttn ShTm ShTTm kst ksht nst nsht pst psht kShT NgkShTh Strry ShThrri rasta astha sTeshon koShTo niShTha proshtho 🙂 ".repeat(64)), "স্ত স্থ স্ট ষ্ট ষ্ঠ শ্ত শ্ত স্টহ্ম শ্তহ্ম শ্তহ্ম স্থম ষ্ঠম স্তন স্তত্ন ষ্টম ষ্টট্ম ক্সত কশত ন্সত নশত প্সত পশত ক্ষট ঙ্ক্ষঠ শ্তরর\u{200d}্য ষ্ঠৃ রাস্তা আস্থা স্টেশন কষ্ট নিষ্ঠা প্রশ্তহ 🙂 ".repeat(64));
}

#[test]
fn ns_ps_ns_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ns.tsv"));
}

#[test]
fn ns_ps_nsh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nsh.tsv"));
}

#[test]
fn ns_ps_ps_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ps.tsv"));
}

#[test]
fn ns_ps_psh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-psh.tsv"));
}

#[test]
fn ns_ps_case_controls_and_consumed_keys_match_exact_unicode() {
    check_fixture(include_str!("fixtures/ns-ps-controls.tsv"));
}

#[test]
fn ns_ps_longer_exceptions_and_priorities_match() {
    for (raw, expected) in [
        ("nsk nsl nsm nsp nsn", "ন্সক ন্সল ন্সম ন্সপ ন্সন"),
        ("psk psl psm psp psn", "প্সক প্সল প্সম প্সপ প্সন"),
        ("nshk nshl nshm nshp nshn", "নশক নশল নশম নশপ নশন"),
        ("pshk pshl pshm pshp pshn", "পশক পশল পশম পশপ পশন"),
        ("nshhl pshhl nssn pssn", "নশহ্ল পশহ্ল ন্সস্ন প্সস্ন"),
        ("nns pnsh snsh shnsh Sns", "ন্নস প্নশ স্নশ শ্নশ শ্নস"),
        ("pps sps Shps mps lps", "প্পস স্পস ষ্পস ম্পস ল্পস"),
        ("nsr nshr psr pshr", "ন্স্র নশ্র প্স্র পশ্র"),
        (
            "nsrri nshrri psrry pshrrZ",
            "ন্সৃ নশৃ প্সরর\u{200d}্য পশরর\u{200d}্য",
        ),
    ] {
        assert_eq!(transliterate(raw), expected, "{raw}");
    }
}

#[test]
fn ns_ps_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("ns", "ন্স", vec![("ন", "স")]),
        ("nsh", "নশ", vec![("ন", "শ"), ("ন্স", "হ")]),
        ("ps", "প্স", vec![("প", "স")]),
        ("psh", "পশ", vec![("প", "শ"), ("প্স", "হ")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "ন্স", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(
        transliterate(
            &"ns nsh ps psh nsk nshl psm pshn nshhl pshhm nssn pssm pnsh mps nsrri pshrry 🙂 "
                .repeat(64)
        ),
        "ন্স নশ প্স পশ ন্সক নশল প্সম পশন নশহ্ল পশহ্ম ন্সস্ন প্সস্ম প্নশ ম্পস ন্সৃ পশরর\u{200d}্য 🙂 ".repeat(64)
    );
}

#[test]
fn repeat_n_bb_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-bb.tsv"));
}

#[test]
fn repeat_n_pp_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-pp.tsv"));
}

#[test]
fn repeat_n_pn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-pn.tsv"));
}

#[test]
fn repeat_n_sn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sn.tsv"));
}

#[test]
fn repeat_n_sh_lowercase_n_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-lowercase-n.tsv"));
}

#[test]
fn repeat_n_s_uppercase_n_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-s-uppercase-n.tsv"));
}

#[test]
fn repeat_n_case_controls_and_consumed_keys_match_exact_unicode() {
    check_fixture(include_str!("fixtures/repeat-n-controls.tsv"));
}

#[test]
fn repeat_n_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("bb", "ব্ব", vec![("ব", "ব")]),
        ("pp", "প্প", vec![("প", "প")]),
        ("pn", "প্ন", vec![("প", "ন")]),
        ("sn", "স্ন", vec![("স", "ন")]),
        ("shn", "শ্ন", vec![("স", "হ্ন"), ("শ", "ন")]),
        ("Sn", "শ্ন", vec![("শ", "ন")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "শ্ন", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(transliterate(&"bb pp pn sn shn Sn bbh pph bbl ppl bbhl pphl pnk snk shnk Snk pnnk snnk shnnk Snnk ksn kshn spn Shpn abbas dhappa shopno snan sneho proshno proSno 🙂 ".repeat(64)), "ব্ব প্প প্ন স্ন শ্ন শ্ন ব্বহ প্পহ ব্বল প্পল ব্বহ্ল প্পহ্ল প্নক স্নক শ্নক শ্নক প্নঙ্ক স্নঙ্ক শ্নঙ্ক শ্নঙ্ক ক্সন কশন স্পন ষ্পন আব্বাস ধাপ্পা শপ্ন স্নান স্নেহ প্রশ্ন প্রশ্ন 🙂 ".repeat(64));
}

#[test]
fn s_labial_sph_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sph.tsv"));
}

#[test]
fn s_labial_spl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-spl.tsv"));
}

#[test]
fn s_labial_sp_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sp.tsv"));
}

#[test]
fn s_labial_sf_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sf.tsv"));
}

#[test]
fn s_labial_sh_ph_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-ph.tsv"));
}

#[test]
fn s_labial_sh_p_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-p.tsv"));
}

#[test]
fn s_labial_sh_f_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-f.tsv"));
}

#[test]
fn s_labial_nonconjunct_and_available_l_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/s-labial-controls.tsv"));
}

#[test]
fn s_labial_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("sph", "স্ফ", vec![("স", "ফ"), ("স্প", "হ")]),
        ("spl", "স্প্ল", vec![("স", "প্ল"), ("স্প", "ল")]),
        ("sp", "স্প", vec![("স", "প")]),
        ("sf", "স্ফ", vec![("স", "ফ")]),
        ("Shph", "ষ্ফ", vec![("শ", "হফ"), ("ষ", "ফ"), ("ষ্প", "হ")]),
        ("Shp", "ষ্প", vec![("শ", "হপ"), ("ষ", "প")]),
        ("Shf", "ষ্ফ", vec![("শ", "হফ"), ("ষ", "ফ")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "স্প্ল", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(transliterate(&"sp sph sf spl Shp Shph Shf spll sphll sfll Shpll Shphll Shfll splg sphlg Shplg splm sphlm ksp kspl kShp NgkShp sphulingo sfUron puShpo niShphol niShfol 🙂 ".repeat(64)), "স্প স্ফ স্ফ স্প্ল ষ্প ষ্ফ ষ্ফ স্প্লল স্ফল্ল স্ফল্ল ষ্পল্ল ষ্ফল্ল ষ্ফল্ল স্প্লগ স্ফল্গ ষ্পল্গ স্প্লম স্ফল্ম ক্সপ ক্সপ্ল ক্ষপ ঙ্ক্ষপ স্ফুলিঙ্গ স্ফূরন পুষ্প নিষ্ফল নিষ্ফল 🙂 ".repeat(64));
}

#[test]
fn l_prefix_lgh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lgh.tsv"));
}

#[test]
fn l_prefix_lg_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lg.tsv"));
}

#[test]
fn l_prefix_lbh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lbh.tsv"));
}

#[test]
fn l_prefix_lb_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lb.tsv"));
}

#[test]
fn l_prefix_lv_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lv.tsv"));
}

#[test]
fn l_prefix_lph_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lph.tsv"));
}

#[test]
fn l_prefix_lp_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lp.tsv"));
}

#[test]
fn l_prefix_l_t_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-l-t-retroflex.tsv"));
}

#[test]
fn l_prefix_l_d_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-l-d-retroflex.tsv"));
}

#[test]
fn l_prefix_ldh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ldh.tsv"));
}

#[test]
fn l_prefix_nonconjunct_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/l-prefix-controls.tsv"));
}

#[test]
fn l_prefix_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("lgh", "লঘ", vec![("ল", "ঘ"), ("ল্গ", "হ")]),
        ("lg", "ল্গ", vec![("ল", "গ")]),
        ("lbh", "ল্ভ", vec![("ল", "ভ"), ("ল্ব", "হ")]),
        ("lb", "ল্ব", vec![("ল", "ব")]),
        ("lv", "ল্ভ", vec![("ল", "ভ")]),
        ("lph", "লফ", vec![("ল", "ফ"), ("ল্প", "হ")]),
        ("lp", "ল্প", vec![("ল", "প")]),
        ("lT", "ল্ট", vec![("ল", "ট")]),
        ("lD", "ল্ড", vec![("ল", "ড")]),
        ("ldh", "ল্ধ", vec![("ল", "ধ"), ("লদ", "হ")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "ল্প", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(transliterate(&"lg lgh lb lbh lv lp lph lT lD ldh lgl lghl lbl lbhl lvl lpl lphl lTm lTh lDD lDh ldhn lghn glg mlg sklgl lfl golpo olpo ulTa 🙂 ".repeat(64)), "ল্গ লঘ ল্ব ল্ভ ল্ভ ল্প লফ ল্ট ল্ড ল্ধ ল্গল লঘল ল্বল ল্ভল ল্ভল ল্পল লফল ল্টম ল্টহ ল্ডড ল্ডহ ল্ধন লঘন গ্লগ ম্লগ স্ক্লগ্ল লফ্ল গল্প অল্প উল্টা 🙂 ".repeat(64));
}

#[test]
fn l_prefix_uppercase_g_stays_separate_from_lowercase_conjunct() {
    assert_eq!(transliterate("lG"), "লগ");
}

#[test]
fn m_labial_mbh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mbh.tsv"));
}

#[test]
fn m_labial_mb_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mb.tsv"));
}

#[test]
fn m_labial_mv_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mv.tsv"));
}

#[test]
fn m_labial_mph_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mph.tsv"));
}

#[test]
fn m_labial_mpl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mpl.tsv"));
}

#[test]
fn m_labial_mp_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mp.tsv"));
}

#[test]
fn m_labial_mf_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mf.tsv"));
}

#[test]
fn m_labial_lm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lm.tsv"));
}

#[test]
fn m_labial_sm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sm.tsv"));
}

#[test]
fn m_labial_sh_lowercase_m_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-lowercase-m.tsv"));
}

#[test]
fn m_labial_s_uppercase_m_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-s-uppercase-m.tsv"));
}

#[test]
fn m_labial_nonconjunct_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/m-labial-controls.tsv"));
}

#[test]
fn m_labial_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("mbh", "ম্ভ", vec![("ম", "ভ"), ("ম্ব", "হ")]),
        ("mb", "ম্ব", vec![("ম", "ব")]),
        ("mv", "ম্ভ", vec![("ম", "ভ")]),
        ("mph", "ম্ফ", vec![("ম", "ফ"), ("ম্প", "হ")]),
        ("mpl", "মপ্ল", vec![("ম", "প্ল"), ("ম্প", "ল")]),
        ("mp", "ম্প", vec![("ম", "প")]),
        ("mf", "ম্ফ", vec![("ম", "ফ")]),
        ("lm", "ল্ম", vec![("ল", "ম")]),
        ("sm", "স্ম", vec![("স", "ম")]),
        ("shm", "শ্ম", vec![("স", "হ্ম"), ("শ", "ম")]),
        ("Sm", "শ্ম", vec![("শ", "ম")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "ম্প", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(transliterate(&"mb mbh mv mp mph mf mpl lm sm shm Sm mbl mbhl mvl mphl mfl mplk mpll mplTm smp shmpl Ngmb kkhmp sklm kshm mbbl mppl 🙂 ".repeat(64)), "ম্ব ম্ভ ম্ভ ম্প ম্ফ ম্ফ মপ্ল ল্ম স্ম শ্ম শ্ম ম্বল ম্ভল ম্ভল ম্ফল ম্ফল মপ্লক মপ্লল মপ্লট্ম স্মপ শ্মপ্ল ঙ্মব ক্ষ্মপ স্ক্লম কশম ম্বব্ল ম্পপ্ল 🙂 ".repeat(64));
}

#[test]
fn l_batch_gl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-gl.tsv"));
}

#[test]
fn l_batch_ll_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ll.tsv"));
}

#[test]
fn l_batch_bl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-bl.tsv"));
}

#[test]
fn l_batch_pl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-pl.tsv"));
}

#[test]
fn l_batch_sl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sl.tsv"));
}

#[test]
fn l_batch_sh_lowercase_l_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-lowercase-l.tsv"));
}

#[test]
fn l_batch_bhl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-bhl.tsv"));
}

#[test]
fn l_batch_phl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-phl.tsv"));
}

#[test]
fn l_batch_vl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-vl.tsv"));
}

#[test]
fn l_batch_fl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-fl.tsv"));
}

#[test]
fn l_batch_s_uppercase_l_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-s-uppercase-l.tsv"));
}

#[test]
fn l_batch_basic_p_following_r_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/p-following-r.tsv"));
}

#[test]
fn l_batch_basic_ph_following_r_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/ph-following-r.tsv"));
}

#[test]
fn l_batch_basic_f_following_r_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/f-following-r.tsv"));
}

#[test]
fn l_batch_nonconjunct_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/l-ending-controls.tsv"));
}

#[test]
fn l_batch_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("gl", "গ্ল", vec![("গ", "ল")]),
        ("ll", "ল্ল", vec![("ল", "ল")]),
        ("bl", "ব্ল", vec![("ব", "ল")]),
        ("pl", "প্ল", vec![("প", "ল")]),
        ("sl", "স্ল", vec![("স", "ল")]),
        ("shl", "শ্ল", vec![("স", "হ্ল"), ("শ", "ল")]),
        ("bhl", "ভ্ল", vec![("ব", "হ্ল"), ("ভ", "ল")]),
        ("phl", "ফ্ল", vec![("প", "হ্ল"), ("ফ", "ল")]),
        ("vl", "ভ্ল", vec![("ভ", "ল")]),
        ("fl", "ফ্ল", vec![("ফ", "ল")]),
        ("Sl", "শ্ল", vec![("শ", "ল")]),
        ("p", "প", vec![]),
        ("ph", "ফ", vec![("প", "হ")]),
        ("f", "ফ", vec![]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "গ্ল", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(
        transliterate(&"gl ll bl pl sl shl bhl phl vl fl Sl pr phr fr blk glk llk slk glpr glphr glfr ggl Nggl kshl skll 🙂 ".repeat(64)),
        "গ্ল ল্ল ব্ল প্ল স্ল শ্ল ভ্ল ফ্ল ভ্ল ফ্ল শ্ল প্র ফ্র ফ্র ব্লক গ্লক ল্লক স্লক গ্লপ্র গ্লফ্র গ্লফ্র জ্ঞল ঙ্গল কশল স্ক্লল 🙂 ".repeat(64)
    );
}

#[test]
fn consuming_k_nkh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nkh.tsv"));
}

#[test]
fn consuming_k_nk_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nk.tsv"));
}

#[test]
fn consuming_k_lkh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lkh.tsv"));
}

#[test]
fn consuming_k_lk_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-lk.tsv"));
}

#[test]
fn consuming_k_skl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-skl.tsv"));
}

#[test]
fn consuming_k_skh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-skh.tsv"));
}

#[test]
fn consuming_k_sk_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sk.tsv"));
}

#[test]
fn consuming_k_sh_k_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-sh-k.tsv"));
}

#[test]
fn consuming_k_ksh_priority_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ksh-priority.tsv"));
}

#[test]
fn consuming_k_ks_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ks.tsv"));
}

#[test]
fn consuming_k_basic_s_following_r_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/s-following-r.tsv"));
}

#[test]
fn consuming_k_basic_sh_following_r_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/sh-lowercase-following-r.tsv"));
}

#[test]
fn consuming_k_basic_s_uppercase_following_r_matches_exact_unicode() {
    check_fixture(include_str!("fixtures/s-uppercase-following-r.tsv"));
}

#[test]
fn consuming_k_case_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consuming-k-controls.tsv"));
}

#[test]
fn consuming_k_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("nkh", "ঙ্খ", vec![("ন", "খ"), ("ঙ্ক", "হ")]),
        ("nk", "ঙ্ক", vec![("ন", "ক")]),
        ("lkh", "লখ", vec![("ল", "খ"), ("ল্ক", "হ")]),
        ("lk", "ল্ক", vec![("ল", "ক")]),
        ("skl", "স্ক্ল", vec![("স", "ক্ল"), ("স্ক", "ল")]),
        ("skh", "স্খ", vec![("স", "খ"), ("স্ক", "হ")]),
        ("sk", "স্ক", vec![("স", "ক")]),
        ("Shk", "ষ্ক", vec![("শ", "হক"), ("ষ", "ক")]),
        ("ksh", "কশ", vec![("ক", "শ"), ("ক্স", "হ")]),
        ("ks", "ক্স", vec![("ক", "স")]),
        ("s", "স", vec![]),
        ("sh", "শ", vec![("স", "হ")]),
        ("S", "শ", vec![]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "স্ক্ল", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(
        transliterate(&"nk nkh lk lkh sk skl skh Shk ks ksh sr shr Sr nktm lktm sktm Shktm skkl nkkh lkkh skkh Shkkh kshm 🙂 ".repeat(64)),
        "ঙ্ক ঙ্খ ল্ক লখ স্ক স্ক্ল স্খ ষ্ক ক্স কশ স্র শ্র শ্র ঙ্কত্ম ল্কত্ম স্কত্ম ষ্কত্ম স্কক্ল ঙ্কখ ল্কখ স্কখ ষ্কখ কশম 🙂 ".repeat(64)
    );
}

#[test]
fn k_batch_kt_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kt.tsv"));
}

#[test]
fn k_batch_k_retroflex_t_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-k-t-retroflex.tsv"));
}

#[test]
fn k_batch_kl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kl.tsv"));
}

#[test]
fn k_batch_nonconjunct_controls_match_exact_unicode() {
    check_fixture(include_str!("fixtures/k-family-controls.tsv"));
}

#[test]
fn k_batch_resets_at_boundaries_and_between_calls() {
    for (raw, bangla, tail) in [("kt", "ক্ত", "ত"), ("kT", "ক্ট", "ট"), ("kl", "ক্ল", "ল")]
    {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "ক্ত", "\u{301}"] {
            assert_eq!(
                transliterate(&format!("k{boundary}{}", &raw[1..])),
                format!("ক{boundary}{tail}")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        assert_eq!(transliterate("k"), "ক");
        assert_eq!(transliterate(&raw[1..]), tail);
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(
        transliterate(&"kt kT kl kn km ktm kTm ktth kth kTh klm Ngkt kkl kShNktr 🙂 ".repeat(64)),
        "ক্ত ক্ট ক্ল কন কম ক্তম ক্টম ক্তথ ক্তহ ক্টহ ক্লম ঙ্কত ক্কল ক্ষ্ণক্ত্র 🙂 ".repeat(64)
    );
}

#[test]
fn t_batch_resets_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("tth", "ত্থ", vec![("ত", "থ"), ("ত্ত", "হ")]),
        ("tt", "ত্ত", vec![("ত", "ত")]),
        ("tn", "ত্ন", vec![("ত", "ন")]),
        ("tm", "ত্ম", vec![("ত", "ম")]),
        ("TT", "ট্ট", vec![("ট", "ট")]),
        ("Tm", "ট্ম", vec![("ট", "ম")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "ত্ত", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(
        transliterate(
            &"tt tth tn tm TT Tm ttth ttn tng tmn TThn ntt nTm nntr kShNTmr 🙂 ".repeat(64)
        ),
        "ত্ত ত্থ ত্ন ত্ম ট্ট ট্ম ত্তথ ত্তন ত্নগ ত্মন ট্টহ্ন ন্তত ন্টম ন্নত্র ক্ষ্ণট্ম্র 🙂 ".repeat(64)
    );
}

#[test]
fn t_batch_tth_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-tth.tsv"));
}

#[test]
fn t_batch_tt_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-tt.tsv"));
}

#[test]
fn t_batch_tn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-tn.tsv"));
}

#[test]
fn t_batch_tm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-tm.tsv"));
}

#[test]
fn t_batch_t_retroflex_pair_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-t-retroflex-pair.tsv"));
}

#[test]
fn t_batch_t_retroflex_m_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-t-retroflex-m.tsv"));
}

#[test]
fn nasal_stops_reset_at_every_split_boundary_and_between_calls() {
    for (raw, bangla, parts) in [
        ("nd", "ন্দ", vec![("ন", "দ")]),
        ("ndh", "ন্ধ", vec![("ন", "ধ"), ("ন্দ", "হ")]),
        ("nD", "ন্ড", vec![("ন", "ড")]),
        ("ND", "ণ্ড", vec![("ণ", "ড")]),
        ("NDh", "ণ্ঢ", vec![("ণ", "ঢ"), ("ণ্ড", "হ")]),
        ("nt", "ন্ত", vec![("ন", "ত")]),
        ("nth", "ন্থ", vec![("ন", "থ"), ("ন্ত", "হ")]),
        ("nT", "ন্ট", vec![("ন", "ট")]),
        ("NT", "ণ্ট", vec![("ণ", "ট")]),
        ("nTh", "ন্ঠ", vec![("ন", "ঠ"), ("ন্ট", "হ")]),
        ("NTh", "ণ্ঠ", vec![("ণ", "ঠ"), ("ণ্ট", "হ")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "ন্দ", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        for (index, (first, tail)) in parts.iter().enumerate() {
            let split = index + 1;
            assert_eq!(transliterate(&raw[..split]), *first);
            assert_eq!(transliterate(&raw[split..]), *tail);
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    for (raw, bangla) in [("t", "ত"), ("th", "থ"), ("T", "ট"), ("Th", "ঠ")] {
        for boundary in ["\n", "\r", "\t", "\0", "🙂", "ত্র"] {
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}a")),
                format!("{bangla}্র{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
        }
    }
    assert_eq!(
        transliterate(
            &"nd ndh nD ND NDh nt nth nT NT nTh NTh nddh ndhn nDh nntr kShNThr 🙂 ".repeat(64)
        ),
        "ন্দ ন্ধ ন্ড ণ্ড ণ্ঢ ন্ত ন্থ ন্ট ণ্ট ন্ঠ ণ্ঠ ন্দধ ন্ধন ন্ডহ ন্নত্র ক্ষ্ণঠ্র 🙂 ".repeat(64)
    );
}

#[test]
fn nasal_stops_conjunct_ndh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ndh.tsv"));
}

#[test]
fn nasal_stops_conjunct_nd_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nd.tsv"));
}

#[test]
fn nasal_stops_conjunct_n_d_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-n-d-retroflex.tsv"));
}

#[test]
fn nasal_stops_conjunct_n_retroflex_dh_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-n-retroflex-dh-retroflex.tsv"
    ));
}

#[test]
fn nasal_stops_conjunct_n_retroflex_d_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-n-retroflex-d-retroflex.tsv"
    ));
}

#[test]
fn nasal_stops_conjunct_nth_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nth.tsv"));
}

#[test]
fn nasal_stops_conjunct_nt_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nt.tsv"));
}

#[test]
fn nasal_stops_conjunct_n_th_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-n-th-retroflex.tsv"));
}

#[test]
fn nasal_stops_conjunct_n_t_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-n-t-retroflex.tsv"));
}

#[test]
fn nasal_stops_conjunct_n_retroflex_th_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-n-retroflex-th-retroflex.tsv"
    ));
}

#[test]
fn nasal_stops_conjunct_n_retroflex_t_retroflex_reference_cases_match_exact_unicode() {
    check_fixture(include_str!(
        "fixtures/conjunct-n-retroflex-t-retroflex.tsv"
    ));
}

#[test]
fn nasal_stops_t_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/t-following-r.tsv"));
}

#[test]
fn nasal_stops_th_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/th-following-r.tsv"));
}

#[test]
fn nasal_stops_t_retroflex_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/t-retroflex-following-r.tsv"));
}

#[test]
fn nasal_stops_th_retroflex_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/th-retroflex-following-r.tsv"));
}

#[test]
fn d_batch_resets_at_boundaries_and_between_calls() {
    for (raw, bangla, parts) in [
        ("dd", "দ্দ", vec![("দ", "দ")]),
        ("ddh", "দ্ধ", vec![("দ", "ধ"), ("দ্দ", "হ")]),
        ("dhn", "ধ্ন", vec![("দ", "হ্ন"), ("ধ", "ন")]),
        ("dhm", "ধ্ম", vec![("দ", "হ্ম"), ("ধ", "ম")]),
        ("dm", "দ্ম", vec![("দ", "ম")]),
        ("dbh", "দ্ভ", vec![("দ", "ভ"), ("দব", "হ")]),
        ("dv", "দ্ভ", vec![("দ", "ভ")]),
        ("DD", "ড্ড", vec![("ড", "ড")]),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "দ্ধ", "\u{301}"] {
            for (index, (first, tail)) in parts.iter().enumerate() {
                let split = index + 1;
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..split], &raw[split..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    for (raw, bangla) in [
        ("d", "দ"),
        ("dh", "ধ"),
        ("D", "ড"),
        ("Dh", "ঢ"),
        ("b", "ব"),
        ("bh", "ভ"),
        ("v", "ভ"),
    ] {
        for boundary in ["\n", "\r", "\t", "\0", "🙂", "দ্র"] {
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}a")),
                format!("{bangla}্র{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("r"), "র");
    }
    assert_eq!(
        transliterate(
            &"dd ddh dhn dhm dm dbh dv DD dr dhr Dr Dhr br bhr vr ddghr dddhr ddbhr DDDhr 🙂 "
                .repeat(64)
        ),
        "দ্দ দ্ধ ধ্ন ধ্ম দ্ম দ্ভ দ্ভ ড্ড দ্র ধ্র ড্র ঢ্র ব্র ভ্র ভ্র দ্দঘ্র দ্দধ্র দ্দভ্র ড্ডঢ্র 🙂 ".repeat(64)
    );
}

#[test]
fn d_batch_conjunct_ddh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ddh.tsv"));
}

#[test]
fn d_batch_conjunct_dd_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-dd.tsv"));
}

#[test]
fn d_batch_conjunct_dhn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-dhn.tsv"));
}

#[test]
fn d_batch_conjunct_dhm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-dhm.tsv"));
}

#[test]
fn d_batch_conjunct_dm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-dm.tsv"));
}

#[test]
fn d_batch_conjunct_dbh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-dbh.tsv"));
}

#[test]
fn d_batch_conjunct_dv_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-dv.tsv"));
}

#[test]
fn d_batch_conjunct_d_retroflex_pair_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-d-retroflex-pair.tsv"));
}

#[test]
fn d_batch_d_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/d-following-r.tsv"));
}

#[test]
fn d_batch_dh_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/dh-following-r.tsv"));
}

#[test]
fn d_batch_d_retroflex_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/d-retroflex-following-r.tsv"));
}

#[test]
fn d_batch_dh_retroflex_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/dh-retroflex-following-r.tsv"));
}

#[test]
fn d_batch_b_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/b-following-r.tsv"));
}

#[test]
fn d_batch_bh_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/bh-following-r.tsv"));
}

#[test]
fn d_batch_v_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/v-following-r.tsv"));
}

#[test]
fn nasal_h_batch_resets_at_boundaries_and_between_calls() {
    assert_eq!(transliterate("mr mm mn mng"), "ম্র ম্ম ম্ন ম্নগ");
    for (raw, bangla, first, tail) in [
        ("ngh", "ঙ্ঘ", "ন", "ঘ"),
        ("nn", "ন্ন", "ন", "ন"),
        ("Nn", "ণ্ন", "ণ", "ন"),
        ("mn", "ম্ন", "ম", "ন"),
        ("hm", "হ্ম", "হ", "ম"),
        ("hl", "হ্ল", "হ", "ল"),
        ("nm", "ন্ম", "ন", "ম"),
        ("Nm", "ণ্ম", "ণ", "ম"),
        ("mm", "ম্ম", "ম", "ম"),
        ("ml", "ম্ল", "ম", "ল"),
        ("Ngm", "ঙ্ম", "ণ", "গ্ম"),
        ("gm", "গ্ম", "গ", "ম"),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "হ্ম", "\u{301}"] {
            assert_eq!(
                transliterate(&format!("{}{boundary}{}", &raw[..1], &raw[1..])),
                format!("{first}{boundary}{tail}")
            );
            if raw == "ngh" || raw == "Ngm" {
                let (first, tail) = if raw == "ngh" {
                    ("ং", "হ")
                } else {
                    ("ঙ", "ম")
                };
                assert_eq!(
                    transliterate(&format!("{}{boundary}{}", &raw[..2], &raw[2..])),
                    format!("{first}{boundary}{tail}")
                );
            }
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    for (raw, bangla) in [("m", "ম"), ("l", "ল")] {
        for boundary in ["\n", "\r", "\t", "\0", "🙂", "ম্র"] {
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}a")),
                format!("{bangla}্র{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("r"), "র");
    }
    assert_eq!(
        transliterate(
            &"ngh nn Nn mn hm hl nm Nm mm ml Ngm gm mr lr Shmmm ShNmng NgkShmr nghnr kShNgmr 🙂 "
                .repeat(64)
        ),
        "ঙ্ঘ ন্ন ণ্ন ম্ন হ্ম হ্ল ন্ম ণ্ম ম্ম ম্ল ঙ্ম গ্ম ম্র ল্র ষ্মম্ম ষ্ণম্নগ ঙ্ক্ষম্র ঙ্ঘন্র ক্ষ্ণগ্ম্র 🙂 ".repeat(64)
    );
}

#[test]
fn nasal_h_conjunct_ngh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ngh.tsv"));
}

#[test]
fn nasal_h_conjunct_n_lower_pair_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-n-lower-pair.tsv"));
}

#[test]
fn nasal_h_conjunct_n_mixed_pair_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-n-mixed-pair.tsv"));
}

#[test]
fn nasal_h_conjunct_mn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mn.tsv"));
}

#[test]
fn nasal_h_conjunct_hm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-hm.tsv"));
}

#[test]
fn nasal_h_conjunct_hl_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-hl.tsv"));
}

#[test]
fn nasal_h_conjunct_nm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nm.tsv"));
}

#[test]
fn nasal_h_conjunct_n_retroflex_m_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-n-retroflex-m.tsv"));
}

#[test]
fn nasal_h_conjunct_mm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-mm.tsv"));
}

#[test]
fn nasal_h_conjunct_ml_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ml.tsv"));
}

#[test]
fn nasal_h_conjunct_ng_m_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ng-m.tsv"));
}

#[test]
fn nasal_h_conjunct_gm_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-gm.tsv"));
}

#[test]
fn nasal_h_m_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/m-following-r.tsv"));
}

#[test]
fn nasal_h_l_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/l-following-r.tsv"));
}

#[test]
fn g_nasal_batch_resets_at_boundaries_and_between_calls() {
    for (raw, bangla, first, tail) in [
        ("gg", "জ্ঞ", "গ", "গ"),
        ("gN", "গ্ণ", "গ", "ণ"),
        ("NN", "ণ্ণ", "ণ", "ণ"),
        ("hN", "হ্ণ", "হ", "ণ"),
        ("gn", "গ্ন", "গ", "ন"),
        ("ghn", "ঘ্ন", "গ", "হ্ন"),
        ("hn", "হ্ন", "হ", "ন"),
        ("dg", "দ্গ", "দ", "গ"),
        ("dgh", "দ্ঘ", "দ", "ঘ"),
        ("Rg", "ড়্গ", "ড়", "গ"),
    ] {
        for boundary in [" ", "\n", "\r", "\t", "\0", "🙂", "জ্ঞ", "\u{301}"] {
            assert_eq!(
                transliterate(&format!("{}{boundary}{}", &raw[..1], &raw[1..])),
                format!("{first}{boundary}{tail}")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(
        transliterate(&"gNgg NNgg hNgg ShNggr kShNgghr dgn Rghn gn ghn hn hr nr Nr 🙂 ".repeat(64)),
        "গ্ণজ্ঞ ণ্ণজ্ঞ হ্ণজ্ঞ ষ্ণজ্ঞ্র ক্ষ্ণজ্ঞহ্র দ্গন ড়্গহ্ন গ্ন ঘ্ন হ্ন হ্র ন্র ণ্র 🙂 ".repeat(64)
    );
}

#[test]
fn conjunct_gg_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-gg.tsv"));
}

#[test]
fn conjunct_g_n_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-g-n.tsv"));
}

#[test]
fn conjunct_nn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nn.tsv"));
}

#[test]
fn conjunct_h_n_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-h-n.tsv"));
}

#[test]
fn conjunct_gn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-gn.tsv"));
}

#[test]
fn conjunct_ghn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ghn.tsv"));
}

#[test]
fn conjunct_hn_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-hn.tsv"));
}

#[test]
fn conjunct_dg_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-dg.tsv"));
}

#[test]
fn conjunct_dgh_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-dgh.tsv"));
}

#[test]
fn conjunct_r_g_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-r-g.tsv"));
}

#[test]
fn h_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/h-following-r.tsv"));
}

#[test]
fn n_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/n-following-r.tsv"));
}

#[test]
fn n_retroflex_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/n-retroflex-following-r.tsv"));
}

#[test]
fn ngg_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ngg.tsv"));
}

#[test]
fn nggh_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-nggh.tsv"));
}

#[test]
fn ngg_nggh_context_resets_at_boundaries_and_between_calls() {
    for (raw, bangla, last) in [("Ngg", "ঙ্গ", "গ"), ("Nggh", "ঙ্ঘ", "ঘ")] {
        for boundary in [' ', '\n', '\r', '\t', '\0', '🙂', 'ঙ', '\u{301}'] {
            assert_eq!(
                transliterate(&format!("Ng{boundary}{}", &raw[2..])),
                format!("ঙ{boundary}{last}")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
    assert_eq!(
        transliterate(&"Ngg Nggh Nggr Ngghr Nggrri Ngghry 🙂 ".repeat(64)),
        "ঙ্গ ঙ্ঘ ঙ্গ্র ঙ্ঘ্র ঙ্গৃ ঙ্ঘ্র্য 🙂 ".repeat(64)
    );
}

#[test]
fn g_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/g-following-r.tsv"));
}

#[test]
fn gh_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/gh-following-r.tsv"));
}

#[test]
fn k_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/k-following-r.tsv"));
}

#[test]
fn kh_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/kh-following-r.tsv"));
}

#[test]
fn sh_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/sh-following-r.tsv"));
}

#[test]
fn basic_following_r_resets_at_boundaries_and_between_calls() {
    for (raw, bangla) in [
        ("k", "ক"),
        ("kh", "খ"),
        ("Sh", "ষ"),
        ("g", "গ"),
        ("gh", "ঘ"),
        ("h", "হ"),
        ("n", "ন"),
        ("N", "ণ"),
    ] {
        for boundary in [' ', '\n', '\r', '\t', '\0', '🙂', 'ক', '\u{301}'] {
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}a")),
                format!("{bangla}্র{boundary}আ")
            );
        }
        assert_eq!(transliterate(&format!("{raw}r")), format!("{bangla}্র"));
        assert_eq!(transliterate("y"), "ইয়");
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
    }
}

#[test]
fn authored_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/reference.tsv"));
}

#[test]
fn vowel_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/vowels.tsv"));
}

#[test]
fn u_vowel_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/vowels-u.tsv"));
}

#[test]
fn long_i_vowel_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/vowels-i-long.tsv"));
}

#[test]
fn e_vowel_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/vowels-e.tsv"));
}

#[test]
fn o_vowel_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/vowels-o.tsv"));
}

#[test]
fn oi_ou_vowel_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/vowels-oi-ou.tsv"));
}

#[test]
fn rri_vowel_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/vowels-rri.tsv"));
}

#[test]
fn r_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonants-r.tsv"));
}

#[test]
fn p_ph_f_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonants-p-ph-f.tsv"));
}

#[test]
fn c_ch_j_jh_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonants-c-ch-j-jh.tsv"));
}

#[test]
fn d_dh_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonants-d-dh.tsv"));
}

#[test]
fn l_h_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonants-l-h.tsv"));
}

#[test]
fn s_sh_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonants-s-sh.tsv"));
}

#[test]
fn retroflex_r_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonants-r-retroflex.tsv"));
}

#[test]
fn z_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonant-z.tsv"));
}

#[test]
fn ng_ng_consonant_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonants-ng-nj.tsv"));
}

#[test]
fn lowercase_ng_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/sign-ng.tsv"));
}

#[test]
fn nasal_rri_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/nasal-rri.tsv"));
}

#[test]
fn uppercase_y_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonant-y-uppercase.tsv"));
}

#[test]
fn lowercase_y_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonant-y-lowercase.tsv"));
}

#[test]
fn uppercase_z_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonant-z-uppercase.tsv"));
}

#[test]
fn ya_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/ya-following-r.tsv"));
}

#[test]
fn uppercase_y_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/uppercase-y-following-r.tsv"));
}

#[test]
fn lowercase_q_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonant-q.tsv"));
}

#[test]
fn lowercase_v_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonant-v.tsv"));
}

#[test]
fn lowercase_w_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonant-w.tsv"));
}

#[test]
fn w_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/w-following-r.tsv"));
}

#[test]
fn lowercase_x_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/consonant-x.tsv"));
}

#[test]
fn x_following_r_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/x-following-r.tsv"));
}

#[test]
fn ngx_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ngx.tsv"));
}

#[test]
fn ngk_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ngk.tsv"));
}

#[test]
fn ngkh_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ngkh.tsv"));
}

#[test]
fn ngkx_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ngkx.tsv"));
}

#[test]
fn ngkkh_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ngkkh.tsv"));
}

#[test]
fn ngksh_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ngksh.tsv"));
}

#[test]
fn kkh_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kkh.tsv"));
}

#[test]
fn ksh_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-ksh.tsv"));
}

#[test]
fn kkhn_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kkhn.tsv"));
}

#[test]
fn kshn_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kshn.tsv"));
}

#[test]
fn kxn_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kxn.tsv"));
}

#[test]
fn kkhm_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kkhm.tsv"));
}

#[test]
fn kshm_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kshm.tsv"));
}

#[test]
fn kxm_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kxm.tsv"));
}

#[test]
fn kk_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-kk.tsv"));
}

#[test]
fn shn_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-shn.tsv"));
}

#[test]
fn shm_conjunct_reference_cases_match_exact_unicode() {
    check_fixture(include_str!("fixtures/conjunct-shm.tsv"));
}

#[test]
fn sh_nasal_context_resets_at_boundaries_and_between_calls() {
    for (raw, bangla, last) in [("ShN", "ষ্ণ", "ণ"), ("Shm", "ষ্ম", "ম")] {
        for boundary in [' ', '\n', '\r', '\t', '\0', '🙂', 'ক', '\u{301}'] {
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("{bangla}{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("Sh{boundary}{}", &raw[2..])),
                format!("ষ{boundary}{last}")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}r")),
                format!("{bangla}{boundary}র")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("{bangla}্র{boundary}ইয়")
            );
        }
        assert_eq!(transliterate(raw), bangla);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
    }
}

#[test]
fn kk_context_resets_at_boundaries_and_between_calls() {
    for boundary in [' ', '\n', '\r', '\t', '\0', '🙂', 'ক', '\u{301}'] {
        assert_eq!(
            transliterate(&format!("kk{boundary}a")),
            format!("ক্ক{boundary}আ")
        );
        assert_eq!(
            transliterate(&format!("k{boundary}k")),
            format!("ক{boundary}ক")
        );
        assert_eq!(
            transliterate(&format!("kk{boundary}r")),
            format!("ক্ক{boundary}র")
        );
    }
    assert_eq!(transliterate("kk"), "ক্ক");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("r"), "র");
    assert_eq!(transliterate("k"), "ক");
}

#[test]
fn m_conjunct_context_resets_at_boundaries_and_between_calls() {
    for raw in ["kkhm", "kShm", "kxm"] {
        for boundary in ['\0', '\n', '\r', '\t', '🙂', 'ক', '\u{301}'] {
            let shorter = &raw[..raw.len() - 1];
            assert_eq!(
                transliterate(&format!("{shorter}{boundary}m")),
                format!("ক্ষ{boundary}ম")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("ক্ষ্ম{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("ক্ষ্ম্র{boundary}ইয়")
            );
        }
        assert_eq!(transliterate(raw), "ক্ষ্ম");
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
        assert_eq!(transliterate("m"), "ম");
    }
}

#[test]
fn n_conjunct_context_resets_at_boundaries_and_between_calls() {
    for raw in ["kkhN", "kShN", "kxN"] {
        for boundary in ['\0', '\n', '\r', '\t', '🙂', 'ক', '\u{301}'] {
            let shorter = &raw[..raw.len() - 1];
            assert_eq!(
                transliterate(&format!("{shorter}{boundary}N")),
                format!("ক্ষ{boundary}ণ")
            );
            assert_eq!(
                transliterate(&format!("{raw}{boundary}a")),
                format!("ক্ষ্ণ{boundary}আ")
            );
            assert_eq!(
                transliterate(&format!("{raw}r{boundary}y")),
                format!("ক্ষ্ণ্র{boundary}ইয়")
            );
        }
        assert_eq!(transliterate(raw), "ক্ষ্ণ");
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("y"), "ইয়");
        assert_eq!(transliterate("N"), "ণ");
    }
}

fn check_fixture(fixture: &str) {
    let mut count = 0;
    for line in fixture.lines() {
        if line.starts_with('#') {
            continue;
        }
        let columns: Vec<_> = line.split('\t').collect();
        assert_eq!(columns.len(), 3, "invalid fixture: {line:?}");
        let [input, expected, points] = [columns[0], columns[1], columns[2]];
        assert_eq!(transliterate(input), expected, "input: {input:?}");
        let actual_points = expected
            .chars()
            .map(|ch| format!("U+{:04X}", ch as u32))
            .collect::<Vec<_>>()
            .join(" ");
        assert_eq!(actual_points, points, "fixture code points: {input:?}");
        count += 1;
    }
    assert!(count > 0, "fixture must contain cases");
}

#[test]
fn empty_input_and_unmatched_unicode_are_preserved() {
    for input in ["", "বাংলা", "é🙂\u{301}", "\t\n !"] {
        assert_eq!(transliterate(input), input);
    }
    assert_eq!(transliterate("qXZ"), "কক্স্য");
    assert_eq!(transliterate("qXYZ"), "কক্সয়্য");
    assert_eq!(transliterate("🙂khবাংলা2é"), "🙂খবাংলা২é");
    // Only ASCII digits are converted; other scripts' digits are preserved.
    assert_eq!(transliterate("০১২৩৪৫৬৭৮৯ ١٢ １２"), "০১২৩৪৫৬৭৮৯ ١٢ １２");
}

#[test]
fn consumed_keys_leave_fresh_g_aliases_and_backtick_boundaries() {
    // An exposed G converts after consumed N; standalone backticks separate matches.
    for raw in ["kkhN", "kShN", "kxN"] {
        assert_eq!(transliterate(&format!("{raw}G")), "ক্ষ্ণগ");
    }
    for raw in ["kkhm", "kShm", "kxm"] {
        assert_eq!(transliterate(&format!("{}M", &raw[..raw.len() - 1])), "ক্ষ্ম");
        assert_eq!(transliterate(&format!("{raw}`a")), "ক্ষ্মআ");
    }
}

#[test]
fn long_mixed_input_preserves_character_boundaries() {
    let input = "🙂kh2a\u{301}kUuakIakeeeakoooakOakOIakOUokrria".repeat(4096)
        + &"rrrirrrri".repeat(4096)
        + &"phifipO".repeat(4096);
    let input =
        input + &"cichijijhi".repeat(4096) + &"didhIDuDhO".repeat(4096) + &"lihU".repeat(4096);
    let input = input + &"sishI SuShO".repeat(4096) + &"RiRhORrri".repeat(4096);
    let input = input + &"zizU".repeat(4096) + &"NgiNGU".repeat(4096);
    let input = input + &"ngang1ngoo".repeat(4096);
    let input = input + &"Ngrri🙂NGrrri1ngrrrri".repeat(4096);
    let input = input + &"YiaYrriY1a".repeat(4096);
    let input = input + &"🙂y🙂ay🙂kya1ryyNgry".repeat(4096);
    let input = input + &"🙂Zi1rZyNgrZa1aZ🙂oZ".repeat(4096);
    let input = input + &"🙂yrr1yrri2yrry3Zry4aZrr".repeat(4096);
    let input = input + &"🙂Yr1Yrri2Yry3Yrry4Yrrrri".repeat(4096);
    let input = input + &"🙂qa1qia2qU3qOI4qrri5qy".repeat(4096);
    let input = input + &"🙂va1via2vU3vOI4vrri5vy".repeat(4096);
    let input = input + &"🙂wa1awa2kwa3wwi4wrri5wy".repeat(4096);
    let input = input + &"🙂wrr1wrri2wrrri3wrry4kwrr5awrr".repeat(4096);
    let input = input + &"🙂xa1axa2kxi3xxU4xrri5xy".repeat(4096);
    let input = input + &"🙂xrr1xrri2xrrri3xrry4kxrr5axrr".repeat(4096);
    let input = input + &"🙂Ngxa1Ngxrri2Ngxrr3Ngxrry4NgxNgx".repeat(4096);
    let input = input + &"🙂Ngka1Ngkr2Ngkrri3Ngkry4Ngkrry5NgkNgk".repeat(4096);
    let input = input + &"🙂Ngkha1Ngkhr2Ngkhrri3Ngkhry4Ngkhrry5NgkhNgkh".repeat(4096);
    let input = input + &"🙂Ngkxa1Ngkxr2Ngkxrri3Ngkxry4Ngkxrr5NgkxNgkx".repeat(4096);
    let input = input + &"🙂Ngkkha1Ngkkhr2Ngkkhrri3Ngkkhry4Ngkkhrry5NgkkhNgkkh".repeat(4096);
    let input = input + &"🙂NgkSha1NgkShr2NgkShrri3NgkShry4NgkShrry5NgkShNgkkh".repeat(4096);
    let input = input + &"🙂kkha1kkhr2kkhrri3kkhry4kkhrry5kkhkkh".repeat(4096);
    let input = input + &"🙂kSha1kShr2kShrri3kShry4kShrry5kShkkh".repeat(4096);
    let input = input + &"🙂kkhNa1kShNr2kxNrri3kxNry4kkhNrry5kShNgkSh".repeat(4096);
    let input = input + &"🙂kkhma1kShmr2kxmrri3kxmry4kkhmrry5kShmng6Ngkxm".repeat(4096);
    let input = input + &"🙂kka1kkr2kkrri3kkry4kkrry5kkkh6kkx7kkhkk".repeat(4096);
    let input = input + &"🙂ShNa1Shmr2ShNrri3Shmry4ShNrry5ShNgx6kkShm7Shmng".repeat(4096);
    let input = input + &"🙂kr1khr2Shr3kry4khrry5ShrrZ6kkkhr7kkShr8Ngkkr".repeat(4096);
    let input = input + &"🙂gr1ghr2gry3ghrry4grri5ShNgr6Shmgr7kShmgr".repeat(4096);
    let expected = "🙂খ২আ\u{301}কূউয়াকীয়াকীএয়াকুঅয়াকোয়াকৈয়াকৌওকৃয়া".repeat(4096)
        + &"রররিররৃ".repeat(4096)
        + &"ফিফিপো".repeat(4096);
    let expected =
        expected + &"চিছিজিঝি".repeat(4096) + &"দিধীডুঢো".repeat(4096) + &"লিহূ".repeat(4096);
    let expected = expected + &"সিশী শুষো".repeat(4096) + &"ড়িঢ়োড়ৃ".repeat(4096);
    let expected = expected + &"যিযূ".repeat(4096) + &"ঙিঞূ".repeat(4096);
    let expected = expected + &"ঙ্গাং১ঙ্গঅ".repeat(4096);
    let expected = expected + &"ঙররি🙂ঞরৃ১ংররররি".repeat(4096);
    let expected = expected + &"য়িয়ায়ৃয়১আ".repeat(4096);
    let expected = expected + &"🙂ইয়🙂আয়🙂ক্যা১র\u{200D}্য্যঙর্য".repeat(4096);
    let expected = expected + &"🙂্যি১র\u{200D}্য্যঙর্যা১অ্যা🙂অ্য".repeat(4096);
    let expected = expected + &"🙂ইয়্রর১ইয়ৃ২ইয়রর\u{200D}্য৩্য্র্য৪অ্যা্রর".repeat(4096);
    let expected = expected + &"🙂য়্র১য়ৃ২য়্র্য৩য়রর\u{200D}্য৪য়্ররৃ".repeat(4096);
    let expected = expected + &"🙂কা১কিয়া২কূ৩কৈ৪কৃ৫ক্য".repeat(4096);
    let expected = expected + &"🙂ভা১ভিয়া২ভূ৩ভৈ৪ভৃ৫ভ্য".repeat(4096);
    let expected = expected + &"🙂ওয়া১আওা২ক্বা৩ও্বি৪ওৃ৫ও্য".repeat(4096);
    let expected = expected + &"🙂ও্রর১ওৃ২ও্রররি৩ওরর\u{200D}্য৪ক্ব্রর৫আও্রর".repeat(4096);
    let expected = expected + &"🙂এক্সা১আক্সা২ক্ষি৩এক্সক্সূ৪এক্সৃ৫এক্স্য".repeat(4096);
    let expected = expected + &"🙂এক্স্রর১এক্সৃ২এক্স্রররি৩এক্সরর\u{200D}্য৪ক্ষ্রর৫আক্স্রর".repeat(4096);
    let expected = expected + &"🙂ঙ্ষা১ঙ্ষৃ২ঙ্ষ্রর৩ঙ্ষরর\u{200D}্য৪ঙ্ষঙ্ষ".repeat(4096);
    let expected = expected + &"🙂ঙ্কা১ঙ্ক্র২ঙ্কৃ৩ঙ্ক্র্য৪ঙ্করর\u{200D}্য৫ঙ্কঙ্ক".repeat(4096);
    let expected = expected + &"🙂ঙ্খা১ঙ্খ্র২ঙ্খৃ৩ঙ্খ্র্য৪ঙ্খরর\u{200D}্য৫ঙ্খঙ্খ".repeat(4096);
    let expected = expected + &"🙂ঙ্ক্ষা১ঙ্ক্ষর২ঙ্ক্ষৃ৩ঙ্ক্ষর\u{200D}্য৪ঙ্ক্ষ্রর৫ঙ্ক্ষঙ্ক্ষ".repeat(4096);
    let expected = expected + &"🙂ঙ্ক্ষা১ঙ্ক্ষ্র২ঙ্ক্ষৃ৩ঙ্ক্ষ্র্য৪ঙ্ক্ষরর\u{200D}্য৫ঙ্ক্ষঙ্ক্ষ".repeat(4096);
    let expected = expected + &"🙂ঙ্ক্ষা১ঙ্ক্ষ্র২ঙ্ক্ষৃ৩ঙ্ক্ষ্র্য৪ঙ্ক্ষরর\u{200D}্য৫ঙ্ক্ষঙ্ক্ষ".repeat(4096);
    let expected = expected + &"🙂ক্ষা১ক্ষ্র২ক্ষৃ৩ক্ষ্র্য৪ক্ষরর\u{200D}্য৫ক্ষক্ষ".repeat(4096);
    let expected = expected + &"🙂ক্ষা১ক্ষ্র২ক্ষৃ৩ক্ষ্র্য৪ক্ষরর\u{200D}্য৫ক্ষক্ষ".repeat(4096);
    let expected = expected + &"🙂ক্ষ্ণা১ক্ষ্ণ্র২ক্ষ্ণৃ৩ক্ষ্ণ্র্য৪ক্ষ্ণরর\u{200D}্য৫ক্ষ্ণগক্ষ".repeat(4096);
    let expected = expected + &"🙂ক্ষ্মা১ক্ষ্ম্র২ক্ষ্মৃ৩ক্ষ্ম্র্য৪ক্ষ্মরর\u{200D}্য৫ক্ষ্মং৬ঙ্ক্ষম".repeat(4096);
    let expected = expected + &"🙂ক্কা১ক্ক্র২ক্কৃ৩ক্ক্র্য৪ক্করর\u{200D}্য৫ক্কখ৬ক্কক্স৭ক্ষক্ক".repeat(4096);
    let expected = expected + &"🙂ষ্ণা১ষ্ম্র২ষ্ণৃ৩ষ্ম্র্য৪ষ্ণরর\u{200D}্য৫ষ্ণগক্স৬ক্কষ্ম৭ষ্মং".repeat(4096);
    let expected =
        expected + &"🙂ক্র১খ্র২ষ্র৩ক্র্য৪খরর\u{200D}্য৫ষরর\u{200D}্য৬ক্কখ্র৭ক্কষ্র৮ঙ্কক্র".repeat(4096);
    let expected = expected + &"🙂গ্র১ঘ্র২গ্র্য৩ঘরর\u{200D}্য৪গৃ৫ষ্ণগ্র৬ষ্মগ্র৭ক্ষ্মগ্র".repeat(4096);
    assert_eq!(transliterate(&input), expected);
}

#[test]
fn vowel_context_resets_at_unmatched_characters_and_between_calls() {
    for boundary in [' ', ',', '-', '\n', '\r', '\t', '🙂', 'ক', '\u{301}'] {
        assert_eq!(
            transliterate(&format!("Y{boundary}r")),
            format!("য়{boundary}র")
        );
        assert_eq!(
            transliterate(&format!("Y{boundary}ry")),
            format!("য়{boundary}র\u{200D}্য")
        );
        assert_eq!(
            transliterate(&format!("r{boundary}Z")),
            format!("র{boundary}্য")
        );
        assert_eq!(
            transliterate(&format!("k{boundary}wa")),
            format!("ক{boundary}ওয়া")
        );
        assert_eq!(
            transliterate(&format!("w{boundary}rr")),
            format!("ও{boundary}রর")
        );
        assert_eq!(
            transliterate(&format!("wrr{boundary}ry")),
            format!("ও্রর{boundary}র\u{200D}্য")
        );
        assert_eq!(
            transliterate(&format!("k{boundary}xa")),
            format!("ক{boundary}এক্সা")
        );
        for (raw, letter) in [
            ("x", "এক্স"),
            ("kx", "ক্ষ"),
            ("Ngx", "ঙ্ষ"),
            ("Ngk", "ঙ্ক"),
            ("Ngkh", "ঙ্খ"),
            ("Ngkx", "ঙ্ক্ষ"),
            ("Ngkkh", "ঙ্ক্ষ"),
            ("NgkSh", "ঙ্ক্ষ"),
            ("kkh", "ক্ষ"),
            ("kSh", "ক্ষ"),
        ] {
            assert_eq!(
                transliterate(&format!("{raw}{boundary}rr")),
                format!("{letter}{boundary}রর")
            );
            assert_eq!(
                transliterate(&format!("{raw}rr{boundary}ry")),
                format!("{letter}্রর{boundary}র\u{200D}্য")
            );
        }
        assert_eq!(
            transliterate(&format!("Ng{boundary}x")),
            format!("ঙ{boundary}এক্স")
        );
        assert_eq!(
            transliterate(&format!("Ng{boundary}k")),
            format!("ঙ{boundary}ক")
        );
        assert_eq!(
            transliterate(&format!("Ngkr{boundary}y")),
            format!("ঙ্ক্র{boundary}ইয়")
        );
        assert_eq!(
            transliterate(&format!("Ngk{boundary}h")),
            format!("ঙ্ক{boundary}হ")
        );
        assert_eq!(
            transliterate(&format!("Ngkh{boundary}r")),
            format!("ঙ্খ{boundary}র")
        );
        assert_eq!(
            transliterate(&format!("Ngkhr{boundary}y")),
            format!("ঙ্খ্র{boundary}ইয়")
        );
        assert_eq!(
            transliterate(&format!("Ngk{boundary}x")),
            format!("ঙ্ক{boundary}এক্স")
        );
        assert_eq!(
            transliterate(&format!("Ngkx{boundary}ry")),
            format!("ঙ্ক্ষ{boundary}র\u{200D}্য")
        );
        assert_eq!(
            transliterate(&format!("Ngkxr{boundary}y")),
            format!("ঙ্ক্ষর{boundary}ইয়")
        );
        assert_eq!(
            transliterate(&format!("Ngk{boundary}kh")),
            format!("ঙ্ক{boundary}খ")
        );
        assert_eq!(
            transliterate(&format!("Ngkkh{boundary}r")),
            format!("ঙ্ক্ষ{boundary}র")
        );
        assert_eq!(
            transliterate(&format!("Ngkkhr{boundary}y")),
            format!("ঙ্ক্ষ্র{boundary}ইয়")
        );
        assert_eq!(
            transliterate(&format!("Ngk{boundary}Sh")),
            format!("ঙ্ক{boundary}ষ")
        );
        assert_eq!(
            transliterate(&format!("NgkSh{boundary}r")),
            format!("ঙ্ক্ষ{boundary}র")
        );
        assert_eq!(
            transliterate(&format!("NgkShr{boundary}y")),
            format!("ঙ্ক্ষ্র{boundary}ইয়")
        );
        assert_eq!(
            transliterate(&format!("k{boundary}kh")),
            format!("ক{boundary}খ")
        );
        assert_eq!(
            transliterate(&format!("kkhr{boundary}y")),
            format!("ক্ষ্র{boundary}ইয়")
        );
        assert_eq!(
            transliterate(&format!("k{boundary}Sh")),
            format!("ক{boundary}ষ")
        );
        assert_eq!(
            transliterate(&format!("kShr{boundary}y")),
            format!("ক্ষ্র{boundary}ইয়")
        );
        for (raw, expected) in [("r", "র"), ("ay", "আয়"), ("ky", "ক্য")] {
            assert_eq!(
                transliterate(&format!("{raw}{boundary}y")),
                format!("{expected}{boundary}ইয়")
            );
        }
        for (vowel, independent) in [
            ("a", "আ"),
            ("i", "ই"),
            ("I", "ঈ"),
            ("u", "উ"),
            ("U", "ঊ"),
            ("e", "এ"),
            ("ee", "ঈ"),
            ("o", "অ"),
            ("O", "ও"),
            ("oo", "উ"),
            ("OI", "ঐ"),
            ("OU", "ঔ"),
            ("rri", "ঋ"),
        ] {
            for (raw, letter) in [
                ("k", "ক"),
                ("q", "ক"),
                ("v", "ভ"),
                ("x", "এক্স"),
                ("kx", "ক্ষ"),
                ("xrr", "এক্স্রর"),
                ("kxrr", "ক্ষ্রর"),
                ("Ngx", "ঙ্ষ"),
                ("Ngxrr", "ঙ্ষ্রর"),
                ("Ngk", "ঙ্ক"),
                ("Ngkr", "ঙ্ক্র"),
                ("Ngkrr", "ঙ্ক্রর"),
                ("Ngkh", "ঙ্খ"),
                ("Ngkhr", "ঙ্খ্র"),
                ("Ngkhrr", "ঙ্খ্রর"),
                ("Ngkx", "ঙ্ক্ষ"),
                ("Ngkxr", "ঙ্ক্ষর"),
                ("Ngkxrr", "ঙ্ক্ষ্রর"),
                ("Ngkkh", "ঙ্ক্ষ"),
                ("Ngkkhr", "ঙ্ক্ষ্র"),
                ("Ngkkhrr", "ঙ্ক্ষ্রর"),
                ("NgkSh", "ঙ্ক্ষ"),
                ("NgkShr", "ঙ্ক্ষ্র"),
                ("NgkShrr", "ঙ্ক্ষ্রর"),
                ("kkh", "ক্ষ"),
                ("kkhr", "ক্ষ্র"),
                ("kkhrr", "ক্ষ্রর"),
                ("kSh", "ক্ষ"),
                ("kShr", "ক্ষ্র"),
                ("kShrr", "ক্ষ্রর"),
                ("w", "ও"),
                ("kw", "ক্ব"),
                ("wrr", "ও্রর"),
                ("kwrr", "ক্ব্রর"),
                ("l", "ল"),
                ("h", "হ"),
                ("s", "স"),
                ("sh", "শ"),
                ("S", "শ"),
                ("Sh", "ষ"),
                ("R", "ড়"),
                ("Rh", "ঢ়"),
                ("z", "য"),
                ("Ng", "ঙ"),
                ("NG", "ঞ"),
                ("ng", "ং"),
                ("Y", "য়"),
                ("y", "ইয়"),
                ("Z", "্য"),
                ("yr", "ইয়র"),
                ("yrr", "ইয়্রর"),
                ("Zry", "্য্র্য"),
                ("Yr", "য়্র"),
                ("Yrr", "য়্রর"),
                ("Yry", "য়্র্য"),
            ] {
                let input = format!("{raw}{boundary}{vowel} {vowel}{boundary}a");
                let expected = format!("{letter}{boundary}{independent} {independent}{boundary}আ");
                assert_eq!(transliterate(&input), expected, "input: {input:?}");
            }
        }
    }
    assert_eq!(transliterate("k"), "ক");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("q"), "ক");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("v"), "ভ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("w"), "ও");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("k"), "ক");
    assert_eq!(transliterate("wa"), "ওয়া");
    assert_eq!(transliterate("i"), "ই");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("I"), "ঈ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("u"), "উ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("U"), "ঊ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("e"), "এ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("ee"), "ঈ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("o"), "অ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("O"), "ও");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("oo"), "উ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("OI"), "ঐ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("OU"), "ঔ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("rri"), "ঋ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("r"), "র");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("rr"), "রর");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("p"), "প");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("ph"), "ফ");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("f"), "ফ");
    assert_eq!(transliterate("a"), "আ");
    for (raw, expected) in [("c", "চ"), ("ch", "ছ"), ("j", "জ"), ("jh", "ঝ")] {
        assert_eq!(transliterate(raw), expected);
        assert_eq!(transliterate("a"), "আ");
    }
    for (raw, expected) in [("d", "দ"), ("dh", "ধ"), ("D", "ড"), ("Dh", "ঢ")] {
        assert_eq!(transliterate(raw), expected);
        assert_eq!(transliterate("a"), "আ");
    }
    for (raw, expected) in [("l", "ল"), ("h", "হ")] {
        assert_eq!(transliterate(raw), expected);
        assert_eq!(transliterate("a"), "আ");
    }
    for (raw, expected) in [("s", "স"), ("sh", "শ"), ("S", "শ"), ("Sh", "ষ")] {
        assert_eq!(transliterate(raw), expected);
        assert_eq!(transliterate("a"), "আ");
    }
    for (raw, expected) in [("R", "ড়"), ("Rh", "ঢ়")] {
        assert_eq!(transliterate(raw), expected);
        assert_eq!(transliterate("a"), "আ");
    }
    assert_eq!(transliterate("z"), "য");
    assert_eq!(transliterate("a"), "আ");
    for (raw, expected) in [("Ng", "ঙ"), ("NG", "ঞ")] {
        assert_eq!(transliterate(raw), expected);
        assert_eq!(transliterate("a"), "আ");
        assert_eq!(transliterate("rri"), "ঋ");
    }
    assert_eq!(transliterate("ng"), "ং");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("rri"), "ঋ");
    assert_eq!(transliterate("Y"), "য়");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("r"), "র");
    assert_eq!(transliterate("y"), "ইয়");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("y"), "ইয়");
    assert_eq!(transliterate("Z"), "্য");
    assert_eq!(transliterate("a"), "আ");
    assert_eq!(transliterate("y"), "ইয়");
    for (raw, expected) in [
        ("yrr", "ইয়্রর"),
        ("Zry", "্য্র্য"),
        ("aZrr", "অ্যা্রর"),
        ("Yr", "য়্র"),
        ("Yrr", "য়্রর"),
        ("Yry", "য়্র্য"),
        ("wrr", "ও্রর"),
        ("kwrr", "ক্ব্রর"),
        ("wrrwrr", "ও্রর্ব্রর"),
        ("x", "এক্স"),
        ("kx", "ক্ষ"),
        ("xrr", "এক্স্রর"),
        ("kxrr", "ক্ষ্রর"),
        ("xrrxrr", "এক্স্ররক্স্রর"),
        ("Ngx", "ঙ্ষ"),
        ("Ngxrr", "ঙ্ষ্রর"),
        ("NgxNgx", "ঙ্ষঙ্ষ"),
        ("Ngk", "ঙ্ক"),
        ("Ngkr", "ঙ্ক্র"),
        ("Ngkrr", "ঙ্ক্রর"),
        ("Ngkry", "ঙ্ক্র্য"),
        ("NgkNgk", "ঙ্কঙ্ক"),
        ("Ngkh", "ঙ্খ"),
        ("Ngkhr", "ঙ্খ্র"),
        ("Ngkhrr", "ঙ্খ্রর"),
        ("Ngkhry", "ঙ্খ্র্য"),
        ("NgkhNgkh", "ঙ্খঙ্খ"),
        ("Ngkx", "ঙ্ক্ষ"),
        ("Ngkxr", "ঙ্ক্ষর"),
        ("Ngkxrr", "ঙ্ক্ষ্রর"),
        ("Ngkxry", "ঙ্ক্ষর\u{200D}্য"),
        ("NgkxNgkx", "ঙ্ক্ষঙ্ক্ষ"),
        ("Ngkkh", "ঙ্ক্ষ"),
        ("Ngkkhr", "ঙ্ক্ষ্র"),
        ("Ngkkhrr", "ঙ্ক্ষ্রর"),
        ("Ngkkhry", "ঙ্ক্ষ্র্য"),
        ("NgkkhNgkkh", "ঙ্ক্ষঙ্ক্ষ"),
        ("NgkSh", "ঙ্ক্ষ"),
        ("NgkShr", "ঙ্ক্ষ্র"),
        ("NgkShrr", "ঙ্ক্ষ্রর"),
        ("NgkShry", "ঙ্ক্ষ্র্য"),
        ("NgkShNgkkh", "ঙ্ক্ষঙ্ক্ষ"),
        ("kkh", "ক্ষ"),
        ("kkhr", "ক্ষ্র"),
        ("kkhrr", "ক্ষ্রর"),
        ("kkhry", "ক্ষ্র্য"),
        ("kkhkkh", "ক্ষক্ষ"),
        ("kSh", "ক্ষ"),
        ("kShr", "ক্ষ্র"),
        ("kShrr", "ক্ষ্রর"),
        ("kShry", "ক্ষ্র্য"),
        ("kShkkh", "ক্ষক্ষ"),
    ] {
        assert_eq!(transliterate(raw), expected);
        assert_eq!(transliterate("r"), "র");
        assert_eq!(transliterate("rr"), "রর");
        assert_eq!(transliterate("y"), "ইয়");
        assert_eq!(transliterate("a"), "আ");
    }
}

#[test]
fn grouped_rule_examples_match_exact_output() {
    assert_eq!(transliterate("t T th Th n N"), "ত ট থ ঠ ন ণ");
    assert_eq!(transliterate("tumi bhUmi kua"), "তুমি ভূমি কুয়া");
    assert_eq!(transliterate("ki kI nIti"), "কি কী নীতি");
    assert_eq!(transliterate("ami ke kee"), "আমি কে কী");
    assert_eq!(transliterate("tumi kemon tOmake"), "তুমি কেমন তোমাকে");
    assert_eq!(transliterate("OI kOI OU kOU nOUka"), "ঐ কৈ ঔ কৌ নৌকা");
    assert_eq!(transliterate("rri krri krriti rriN"), "ঋ কৃ কৃতি ঋণ");
    assert_eq!(transliterate("ram rani rrri rrrri"), "রাম রানি রররি ররৃ");
    assert_eq!(transliterate("pani phOn fOn"), "পানি ফোন ফোন");
    assert_eq!(transliterate("cabi chabi jani jhuri"), "চাবি ছাবি জানি ঝুরি");
    assert_eq!(transliterate("din dhan Dan Dhaka"), "দিন ধান ডান ঢাকা");
    assert_eq!(transliterate("lal holud bhalO"), "লাল হলুদ ভালো");
    assert_eq!(transliterate("sokal shishu SiSu bhaSha"), "সকাল শিশু শিশু ভাষা");
    assert_eq!(transliterate("baRi gaRi gaRh drriRh"), "বাড়ি গাড়ি গাঢ় দৃঢ়");
    assert_eq!(transliterate("zai zabe zodi zokhon"), "যাই যাবে যদি যখন");
    assert_eq!(transliterate("Ng NG aNgul raNga"), "ঙ ঞ আঙুল রাঙা");
    assert_eq!(transliterate("bangla rong nga ngi"), "বাংলা রং ঙ্গা ঙ্গি");
    assert_eq!(transliterate("Ngrri NGrrri ngrrrri"), "ঙররি ঞরৃ ংররররি");
    assert_eq!(transliterate("zaY hoY hoYe maYa"), "যায় হয় হয়ে মায়া");
    assert_eq!(transliterate("y ay ky kiya"), "ইয় আয় ক্য কিয়া");
    assert_eq!(transliterate("kZa aZ oZ baZ"), "ক্যা অ্যা অ্য বঅ্যা");
    assert_eq!(
        transliterate("yrr yrri yry Zry"),
        "ইয়্রর ইয়ৃ ইয়র\u{200D}্য ্য্র্য"
    );
    assert_eq!(transliterate("Yr Yrri Yry Yrry"), "য়্র য়ৃ য়্র্য য়রর\u{200D}্য");
    assert_eq!(transliterate("q qa qi qOI qotha"), "ক কা কি কৈ কথা");
    assert_eq!(transliterate("v vi vU valO vUmi"), "ভ ভি ভূ ভালো ভূমি");
    assert_eq!(transliterate("w wa awa kw kwa"), "ও ওয়া আওা ক্ব ক্বা");
    assert_eq!(
        transliterate("wr wrri wrrri wrry"),
        "ওর ওৃ ও্রররি ওরর\u{200D}্য"
    );
    assert_eq!(transliterate("x xa axa kx kxa"), "এক্স এক্সা আক্সা ক্ষ ক্ষা");
    assert_eq!(
        transliterate("xr xrr xrri xrrri kxrr"),
        "এক্সর এক্স্রর এক্সৃ এক্স্রররি ক্ষ্রর"
    );
    assert_eq!(transliterate("Ngx Ngxa Ngxrri Ngxrr"), "ঙ্ষ ঙ্ষা ঙ্ষৃ ঙ্ষ্রর");
    assert_eq!(transliterate("Ngk Ngka Ngkr Ngkrri"), "ঙ্ক ঙ্কা ঙ্ক্র ঙ্কৃ");
    assert_eq!(transliterate("Ngkh Ngkha Ngkhr Ngkhrri"), "ঙ্খ ঙ্খা ঙ্খ্র ঙ্খৃ");
    assert_eq!(
        transliterate("Ngkx Ngkxa Ngkxrri Ngkxrr"),
        "ঙ্ক্ষ ঙ্ক্ষা ঙ্ক্ষৃ ঙ্ক্ষ্রর"
    );
    assert_eq!(
        transliterate("Ngkkh Ngkkha Ngkkhr Ngkkhrri"),
        "ঙ্ক্ষ ঙ্ক্ষা ঙ্ক্ষ্র ঙ্ক্ষৃ"
    );
    assert_eq!(
        transliterate("NgkSh NgkSha NgkShr NgkShrri"),
        "ঙ্ক্ষ ঙ্ক্ষা ঙ্ক্ষ্র ঙ্ক্ষৃ"
    );
    assert_eq!(transliterate("kkh kkha kkhr kkhrri"), "ক্ষ ক্ষা ক্ষ্র ক্ষৃ");
    assert_eq!(transliterate("kSh kSha kShr kShrri"), "ক্ষ ক্ষা ক্ষ্র ক্ষৃ");
    assert_eq!(transliterate("kkhN kShNa kxNr kxNrri"), "ক্ষ্ণ ক্ষ্ণা ক্ষ্ণ্র ক্ষ্ণৃ");
    assert_eq!(transliterate("kkhm kShma kxmr kxmrri"), "ক্ষ্ম ক্ষ্মা ক্ষ্ম্র ক্ষ্মৃ");
    assert_eq!(
        transliterate("kk kka kkr kkrri kkkh kkx"),
        "ক্ক ক্কা ক্ক্র ক্কৃ ক্কখ ক্কক্স"
    );
    assert_eq!(
        transliterate("ShN Shm ShNr Shmrri kkShN ShNgx"),
        "ষ্ণ ষ্ম ষ্ণ্র ষ্মৃ ক্কষ্ণ ষ্ণগক্স"
    );
    assert_eq!(
        transliterate("kr khr Shr kry krry kkkhr kkShr Ngkkr"),
        "ক্র খ্র ষ্র ক্র্য করর‍্য ক্কখ্র ক্কষ্র ঙ্কক্র"
    );
    assert_eq!(
        transliterate("gr ghr gry ghrry grri ShNgr Shmgr"),
        "গ্র ঘ্র গ্র্য ঘরর‍্য গৃ ষ্ণগ্র ষ্মগ্র"
    );
    assert_eq!(
        transliterate("Ngg Nggh Nggr Ngghr Nggrri Ngghry"),
        "ঙ্গ ঙ্ঘ ঙ্গ্র ঙ্ঘ্র ঙ্গৃ ঙ্ঘ্র্য"
    );
    assert_eq!(
        transliterate("gg gN NN hN gn ghn hn dg dgh Rg"),
        "জ্ঞ গ্ণ ণ্ণ হ্ণ গ্ন ঘ্ন হ্ন দ্গ দ্ঘ ড়্গ"
    );
    assert_eq!(
        transliterate("ngh nn Nn mn hm hl nm Nm mm ml Ngm gm mr lr"),
        "ঙ্ঘ ন্ন ণ্ন ম্ন হ্ম হ্ল ন্ম ণ্ম ম্ম ম্ল ঙ্ম গ্ম ম্র ল্র"
    );
    assert_eq!(
        transliterate("dd ddh dhn dhm dm dbh dv DD dr dhr Dr Dhr br bhr vr"),
        "দ্দ দ্ধ ধ্ন ধ্ম দ্ম দ্ভ দ্ভ ড্ড দ্র ধ্র ড্র ঢ্র ব্র ভ্র ভ্র"
    );
    assert_eq!(
        transliterate("nd ndh nD ND NDh nt nth nT NT nTh NTh tr thr Tr Thr"),
        "ন্দ ন্ধ ন্ড ণ্ড ণ্ঢ ন্ত ন্থ ন্ট ণ্ট ন্ঠ ণ্ঠ ত্র থ্র ট্র ঠ্র"
    );
    assert_eq!(
        transliterate("tt tth tn tm TT Tm uttor utthan rotno atma"),
        "ত্ত ত্থ ত্ন ত্ম ট্ট ট্ম উত্তর উত্থান রত্ন আত্মা"
    );
    assert_eq!(
        transliterate("kt kT kl kn km ktm kTm rokto klanto"),
        "ক্ত ক্ট ক্ল কন কম ক্তম ক্টম রক্ত ক্লান্ত"
    );
    assert_eq!(
        transliterate("nk nkh lk lkh sk skl skh Shk ks ksh sr shr Sr"),
        "ঙ্ক ঙ্খ ল্ক লখ স্ক স্ক্ল স্খ ষ্ক ক্স কশ স্র শ্র শ্র"
    );
    assert_eq!(
        transliterate("gl ll bl pl sl shl bhl phl vl fl Sl pr phr fr"),
        "গ্ল ল্ল ব্ল প্ল স্ল শ্ল ভ্ল ফ্ল ভ্ল ফ্ল শ্ল প্র ফ্র ফ্র"
    );
    assert_eq!(
        transliterate("mb mbh mv mp mph mf mpl lm sm shm Sm mbl mplk smp"),
        "ম্ব ম্ভ ম্ভ ম্প ম্ফ ম্ফ মপ্ল ল্ম স্ম শ্ম শ্ম ম্বল মপ্লক স্মপ"
    );
}

#[test]
fn audit_interactions_match_exact_unicode() {
    check_fixture(include_str!("fixtures/audit-interactions.tsv"));
}
