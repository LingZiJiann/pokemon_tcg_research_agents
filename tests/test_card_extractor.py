import pytest

from src.tools.card_extractor import extract_card_name


class TestExtractCardName:
    """Test suite for extract_card_name function."""

    # Graded conditions tests
    def test_psa_graded_condition(self):
        result = extract_card_name("Charizard PSA 10")
        assert result["name"] == "charizard"
        assert result["condition"] == "psa 10"

    def test_bgs_graded_condition(self):
        result = extract_card_name("Black Lotus BGS 9.5")
        assert result["name"] == "black lotus"
        assert result["condition"] == "bgs 9.5"

    def test_cgc_graded_condition(self):
        result = extract_card_name("Blastoise CGC 8")
        assert result["name"] == "blastoise"
        assert result["condition"] == "cgc 8"

    def test_graded_condition_case_insensitive(self):
        result = extract_card_name("pikachu psa 9")
        assert result["name"] == "pikachu"
        assert result["condition"] == "psa 9"

    def test_graded_condition_with_space_variations(self):
        result1 = extract_card_name("Dragonite PSA10")
        result2 = extract_card_name("Dragonite PSA 10")
        assert result1["condition"] == "psa 10"
        assert result2["condition"] == "psa 10"

    # Ungraded condition tests
    def test_nm_condition(self):
        result = extract_card_name("Alakazam NM")
        assert result["name"] == "alakazam"
        assert result["condition"] == "nm"

    def test_nm_mt_condition(self):
        result = extract_card_name("Machamp NM-MT")
        assert result["name"] == "machamp"
        assert result["condition"] == "nm-mt"

    def test_near_mint_condition(self):
        result = extract_card_name("Golem Near Mint")
        assert result["name"] == "golem"
        assert result["condition"] == "nm"

    def test_lightly_played_condition(self):
        result = extract_card_name("Arcanine Lightly Played")
        assert result["name"] == "arcanine"
        assert result["condition"] == "lp"

    def test_lp_condition(self):
        result = extract_card_name("Lapras LP")
        assert result["name"] == "lapras"
        assert result["condition"] == "lp"

    def test_mp_condition(self):
        result = extract_card_name("Raichu MP")
        assert result["name"] == "raichu"
        assert result["condition"] == "mp"

    def test_hp_condition(self):
        result = extract_card_name("Gengar HP")
        assert result["name"] == "gengar"
        assert result["condition"] == "hp"

    def test_dmg_condition(self):
        result = extract_card_name("Exeggutor DMG")
        assert result["name"] == "exeggutor"
        assert result["condition"] == "dmg"

    def test_ungraded_condition_case_insensitive(self):
        result = extract_card_name("articuno nm")
        assert result["name"] == "articuno"
        assert result["condition"] == "nm"

    # Default condition tests
    def test_default_raw_condition(self):
        result = extract_card_name("Meowth")
        assert result["name"] == "meowth"
        assert result["condition"] == "raw"

    def test_default_raw_with_numbers(self):
        result = extract_card_name("Base Set Charizard 4/102")
        assert result["name"] == "base set charizard 4/102"
        assert result["condition"] == "raw"

    # Name normalization tests
    def test_name_whitespace_normalization(self):
        result = extract_card_name("pikachu    NM")
        assert result["name"] == "pikachu"

    def test_name_with_multiple_spaces_between_words(self):
        result = extract_card_name("base  set   charizard  psa 10")
        assert result["name"] == "base set charizard"
        assert result["condition"] == "psa 10"

    # Priority tests (graded should take precedence over ungraded)
    def test_graded_takes_priority_over_ungraded(self):
        result = extract_card_name("Venusaur PSA 8 NM")
        assert result["condition"] == "psa 8"

    # Edge cases
    def test_empty_string(self):
        result = extract_card_name("")
        assert result["name"] == ""
        assert result["condition"] == "raw"

    def test_only_condition_psa(self):
        result = extract_card_name("PSA 10")
        assert result["name"] == ""
        assert result["condition"] == "psa 10"

    def test_only_condition_nm(self):
        result = extract_card_name("NM")
        assert result["name"] == ""
        assert result["condition"] == "nm"

    def test_decimal_grade(self):
        result = extract_card_name("Lugia BGS 8.5")
        assert result["name"] == "lugia"
        assert result["condition"] == "bgs 8.5"

    def test_special_characters_in_name(self):
        result = extract_card_name("Articuno-Ex PSA 9")
        assert result["name"] == "articuno-ex"
        assert result["condition"] == "psa 9"

    def test_name_with_parentheses(self):
        result = extract_card_name("Lugia (Secret) NM")
        assert result["name"] == "lugia (secret)"
        assert result["condition"] == "nm"

    def test_condition_at_beginning(self):
        result = extract_card_name("NM Charizard")
        assert result["name"] == "charizard"
        assert result["condition"] == "nm"

    def test_condition_in_middle(self):
        result = extract_card_name("Charizard PSA 10 Secret Rare")
        assert result["name"] == "charizard secret rare"
        assert result["condition"] == "psa 10"

    def test_multiple_grades_input(self):
        result = extract_card_name("Charizard PSA 10 BGS 10 CGC 9.5")
        assert result["name"] == "charizard"
        assert result["condition"] == "psa 10"
