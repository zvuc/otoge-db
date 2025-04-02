GAME_NAME = "chunithm"

CURRENT_JP_VER = "VERSE"
CURRENT_INTL_VER = "LUMINOUS PLUS"

HASH_KEYS = ['image']
HASH_KEYS_SP = ['image', 'we_kanji']

META_KEYS = {
    "artist",
    "title",
    "reading"
}

LEVEL_KEYS = {
    "lev_bas",
    "lev_adv",
    "lev_exp",
    "lev_mas",
    "lev_ult",
    "we_kanji",
    "we_star"
}

LEVEL_CONST_KEYS = {
    "lev_bas_i",
    "lev_adv_i",
    "lev_exp_i",
    "lev_mas_i",
    "lev_ult_i"
}

OTHER_KEYS = {
    "id",
    "catname",
    "image"
}

IGNORE_KEYS = {
}

NEW_TAG_KEY = "newflag"

REQUIRED_KEYS_PER_CHART = {
    "lev_bas": ["lev_bas_i", "lev_bas_notes","lev_bas_notes_tap","lev_bas_notes_hold","lev_bas_notes_slide","lev_bas_notes_air","lev_bas_notes_chart_link"],
    "lev_adv": ["lev_adv_i", "lev_adv_notes","lev_adv_notes_tap","lev_adv_notes_hold","lev_adv_notes_slide","lev_adv_notes_air","lev_adv_notes_chart_link"],
    "lev_exp": ["lev_exp_i", "lev_exp_notes","lev_exp_notes_tap","lev_exp_notes_hold","lev_exp_notes_slide","lev_exp_notes_air","lev_exp_notes_flick","lev_exp_designer","lev_exp_notes_chart_link"],
    "lev_mas": ["lev_mas_i", "lev_mas_notes","lev_mas_notes_tap","lev_mas_notes_hold","lev_mas_notes_slide","lev_mas_notes_air","lev_mas_notes_flick","lev_mas_designer","lev_mas_notes_chart_link"],
    "lev_ult": ["lev_ult_i", "lev_ult_notes","lev_ult_notes_tap","lev_ult_notes_hold","lev_ult_notes_slide","lev_ult_notes_air","lev_ult_notes_flick","lev_ult_designer","lev_ult_notes_chart_link"],
    "we_kanji": ["lev_we_notes","lev_we_notes_tap","lev_we_notes_hold","lev_we_notes_slide","lev_we_notes_air","lev_we_notes_touch","lev_we_designer","lev_we_notes_chart_link"]
}

KEY_ORDER = [
    "id",
    "catname",
    "newflag",
    "title",
    "reading",
    "artist",
    "lev_bas",
    "lev_adv",
    "lev_exp",
    "lev_mas",
    "lev_ult",
    "we_kanji",
    "we_star",
    "image",
    "bpm",
    "lev_bas_i",
    "lev_bas_notes",
    "lev_bas_notes_tap",
    "lev_bas_notes_hold",
    "lev_bas_notes_slide",
    "lev_bas_notes_air",
    "lev_bas_notes_flick",
    "lev_adv_i",
    "lev_adv_notes",
    "lev_adv_notes_tap",
    "lev_adv_notes_hold",
    "lev_adv_notes_slide",
    "lev_adv_notes_air",
    "lev_adv_notes_flick",
    "lev_exp_i",
    "lev_exp_notes",
    "lev_exp_notes_tap",
    "lev_exp_notes_hold",
    "lev_exp_notes_slide",
    "lev_exp_notes_air",
    "lev_exp_notes_flick",
    "lev_exp_designer",
    "lev_exp_chart_link",
    "lev_mas_i",
    "lev_mas_notes",
    "lev_mas_notes_tap",
    "lev_mas_notes_hold",
    "lev_mas_notes_slide",
    "lev_mas_notes_air",
    "lev_mas_notes_flick",
    "lev_mas_designer",
    "lev_mas_chart_link",
    "lev_ult_i",
    "lev_ult_notes",
    "lev_ult_notes_tap",
    "lev_ult_notes_hold",
    "lev_ult_notes_slide",
    "lev_ult_notes_air",
    "lev_ult_notes_flick",
    "lev_ult_designer",
    "lev_ult_chart_link",
    "lev_we_notes",
    "lev_we_notes_tap",
    "lev_we_notes_hold",
    "lev_we_notes_slide",
    "lev_we_notes_air",
    "lev_we_notes_flick",
    "lev_we_designer",
    "lev_we_chart_link",
    "version",
    "wikiwiki_url",
    "intl",
    "date_added",
    "date_updated",
    "date_intl_added",
    "date_intl_updated"
]
