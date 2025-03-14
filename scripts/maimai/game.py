GAME_NAME = "maimai"

CURRENT_JP_VER = "PRiSM PLUS"
CURRENT_INTL_VER = "PRiSM"

HASH_KEYS = ['title', 'image_url']
HASH_KEYS_UTAGE = ['title', 'lev_utage', 'kanji']

LEVEL_KEYS = {
    "lev_bas",
    "lev_adv",
    "lev_exp",
    "lev_mas",
    "lev_remas",
    "dx_lev_bas",
    "dx_lev_adv",
    "dx_lev_exp",
    "dx_lev_mas",
    "dx_lev_remas"
}

LEVEL_CONST_KEYS = {
    "lev_bas_i",
    "lev_adv_i",
    "lev_exp_i",
    "lev_mas_i",
    "lev_remas_i",
    "dx_lev_bas_i",
    "dx_lev_adv_i",
    "dx_lev_exp_i",
    "dx_lev_mas_i",
    "dx_lev_remas_i"
}

OTHER_KEYS = {
    "artist",
    "catcode",
    "kanji",
    "comment",
    "image_url",
    "key",
    "release",
    "title",
    "title_kana",
    "version"
}

IGNORE_KEYS = {
}

NEW_TAG_KEY = "date"

CHART_LIST = [
    "lev_bas",
    "lev_adv",
    "lev_exp",
    "lev_mas",
    "lev_remas"
]

CHART_LIST_DX = [
    "dx_lev_bas",
    "dx_lev_adv",
    "dx_lev_exp",
    "dx_lev_mas",
    "dx_lev_remas"
]

REQUIRED_KEYS_PER_CHART = {
    "lev_bas": ["lev_bas_notes","lev_bas_notes_tap","lev_bas_notes_hold","lev_bas_notes_slide","lev_bas_notes_break"],
    "lev_adv": ["lev_adv_notes","lev_adv_notes_tap","lev_adv_notes_hold","lev_adv_notes_slide","lev_adv_notes_break"],
    "lev_exp": ["lev_exp_notes","lev_exp_notes_tap","lev_exp_notes_hold","lev_exp_notes_slide","lev_exp_notes_break","lev_exp_designer"],
    "lev_mas": ["lev_mas_notes","lev_mas_notes_tap","lev_mas_notes_hold","lev_mas_notes_slide","lev_mas_notes_break","lev_mas_designer"],
    "lev_remas": ["lev_remas_notes","lev_remas_notes_tap","lev_remas_notes_hold","lev_remas_notes_slide","lev_remas_notes_break","lev_remas_designer"],
    "dx_lev_bas": ["dx_lev_bas_notes","dx_lev_bas_notes_tap","dx_lev_bas_notes_hold","dx_lev_bas_notes_slide","dx_lev_bas_notes_break","dx_lev_bas_notes_touch"],
    "dx_lev_adv": ["dx_lev_adv_notes","dx_lev_adv_notes_tap","dx_lev_adv_notes_hold","dx_lev_adv_notes_slide","dx_lev_adv_notes_break","dx_lev_adv_notes_touch"],
    "dx_lev_exp": ["dx_lev_exp_notes","dx_lev_exp_notes_tap","dx_lev_exp_notes_hold","dx_lev_exp_notes_slide","dx_lev_exp_notes_break","dx_lev_exp_notes_touch","dx_lev_exp_designer"],
    "dx_lev_mas": ["dx_lev_mas_notes","dx_lev_mas_notes_tap","dx_lev_mas_notes_hold","dx_lev_mas_notes_slide","dx_lev_mas_notes_break","dx_lev_mas_notes_touch","dx_lev_mas_designer"],
    "dx_lev_remas": ["dx_lev_remas_notes","dx_lev_remas_notes_tap","dx_lev_remas_notes_hold","dx_lev_remas_notes_slide","dx_lev_remas_notes_break","dx_lev_remas_notes_touch","dx_lev_remas_designer"],
    "lev_utage": ["lev_utage_notes","lev_utage_notes_tap","lev_utage_notes_hold","lev_utage_notes_slide","lev_utage_notes_break","lev_utage_notes_touch","lev_utage_designer"]
}

KEY_ORDER = [
    "sort",
    "title",
    "title_kana",
    "artist",
    "catcode",
    "version",
    "bpm",
    "image_url",
    "release",
    "lev_bas",
    "lev_adv",
    "lev_exp",
    "lev_mas",
    "lev_remas",
    "lev_utage",
    "dx_lev_bas",
    "dx_lev_adv",
    "dx_lev_exp",
    "dx_lev_mas",
    "dx_lev_remas",
    "lev_bas_i",
    "lev_bas_notes",
    "lev_bas_notes_tap",
    "lev_bas_notes_hold",
    "lev_bas_notes_slide",
    "lev_bas_notes_break",
    "lev_adv_i",
    "lev_adv_notes",
    "lev_adv_notes_tap",
    "lev_adv_notes_hold",
    "lev_adv_notes_slide",
    "lev_adv_notes_break",
    "lev_exp_i",
    "lev_exp_notes",
    "lev_exp_notes_tap",
    "lev_exp_notes_hold",
    "lev_exp_notes_slide",
    "lev_exp_notes_break",
    "lev_exp_designer",
    "lev_mas_i",
    "lev_mas_notes",
    "lev_mas_notes_tap",
    "lev_mas_notes_hold",
    "lev_mas_notes_slide",
    "lev_mas_notes_break",
    "lev_mas_designer",
    "lev_remas_i",
    "lev_remas_notes",
    "lev_remas_notes_tap",
    "lev_remas_notes_hold",
    "lev_remas_notes_slide",
    "lev_remas_notes_break",
    "lev_remas_designer",
    "dx_lev_bas_i",
    "dx_lev_bas_notes",
    "dx_lev_bas_notes_tap",
    "dx_lev_bas_notes_hold",
    "dx_lev_bas_notes_slide",
    "dx_lev_bas_notes_touch",
    "dx_lev_bas_notes_break",
    "dx_lev_adv_i",
    "dx_lev_adv_notes",
    "dx_lev_adv_notes_tap",
    "dx_lev_adv_notes_hold",
    "dx_lev_adv_notes_slide",
    "dx_lev_adv_notes_touch",
    "dx_lev_adv_notes_break",
    "dx_lev_exp_i",
    "dx_lev_exp_notes",
    "dx_lev_exp_notes_tap",
    "dx_lev_exp_notes_hold",
    "dx_lev_exp_notes_slide",
    "dx_lev_exp_notes_touch",
    "dx_lev_exp_notes_break",
    "dx_lev_exp_designer",
    "dx_lev_mas_i",
    "dx_lev_mas_notes",
    "dx_lev_mas_notes_tap",
    "dx_lev_mas_notes_hold",
    "dx_lev_mas_notes_slide",
    "dx_lev_mas_notes_touch",
    "dx_lev_mas_notes_break",
    "dx_lev_mas_designer",
    "dx_lev_remas_i",
    "dx_lev_remas_notes",
    "dx_lev_remas_notes_tap",
    "dx_lev_remas_notes_hold",
    "dx_lev_remas_notes_slide",
    "dx_lev_remas_notes_touch",
    "dx_lev_remas_notes_break",
    "dx_lev_remas_designer",
    "lev_utage_notes",
    "lev_utage_notes_tap",
    "lev_utage_notes_hold",
    "lev_utage_notes_slide",
    "lev_utage_notes_break",
    "lev_utage_designer",
    "kanji",
    "comment",
    "wiki_url",
    "intl",
    "key",
    "key_intl",
    "date_added",
    "date_updated",
    "date_intl_added",
    "date_intl_updated"
]
