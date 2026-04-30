import pytest

from src.tools.card_extractor import extract_card_name


class TestExtractCardName:
    """Test suite for extract_card_name function."""

    # Graded conditions tests
    def test_psa_graded_condition(self):
        result = extract_card_name("Charizard PSA 10")
        assert result["name"] == "Charizard"
        assert result["condition"] == "PSA 10"

    def test_bgs_graded_condition(self):
        result = extract_card_name("Black Lotus BGS 9.5")
        assert result["name"] == "Black Lotus"
        assert result["condition"] == "BGS 9.5"

    def test_cgc_graded_condition(self):
        result = extract_card_name("Blastoise CGC 8")
        assert result["name"] == "Blastoise"
        assert result["condition"] == "CGC 8"

    def test_graded_condition_case_insensitive(self):
        result = extract_card_name("pikachu psa 9")
        assert result["name"] == "Pikachu"
        assert result["condition"] == "PSA 9"

    def test_graded_condition_with_space_variations(self):
        result1 = extract_card_name("Dragonite PSA10")
        result2 = extract_card_name("Dragonite PSA 10")
        assert result1["condition"] == "PSA 10"
        assert result2["condition"] == "PSA 10"

    # Ungraded condition tests
    def test_nm_condition(self):
        result = extract_card_name("Alakazam NM")
        assert result["name"] == "Alakazam"
        assert result["condition"] == "NM"

    def test_nm_mt_condition(self):
        result = extract_card_name("Machamp NM-MT")
        assert result["name"] == "Machamp"
        assert result["condition"] == "NM-MT"

    def test_near_mint_condition(self):
        result = extract_card_name("Golem Near Mint")
        assert result["name"] == "Golem"
        assert result["condition"] == "NM"

    def test_lightly_played_condition(self):
        result = extract_card_name("Arcanine Lightly Played")
        assert result["name"] == "Arcanine"
        assert result["condition"] == "LP"

    def test_lp_condition(self):
        result = extract_card_name("Lapras LP")
        assert result["name"] == "Lapras"
        assert result["condition"] == "LP"

    def test_mp_condition(self):
        result = extract_card_name("Raichu MP")
        assert result["name"] == "Raichu"
        assert result["condition"] == "MP"

    def test_hp_condition(self):
        result = extract_card_name("Gengar HP")
        assert result["name"] == "Gengar"
        assert result["condition"] == "HP"

    def test_dmg_condition(self):
        result = extract_card_name("Exeggutor DMG")
        assert result["name"] == "Exeggutor"
        assert result["condition"] == "DMG"

    def test_ungraded_condition_case_insensitive(self):
        result = extract_card_name("articuno nm")
        assert result["name"] == "Articuno"
        assert result["condition"] == "NM"

    # Default condition tests
    def test_default_raw_condition(self):
        result = extract_card_name("Meowth")
        assert result["name"] == "Meowth"
        assert result["condition"] == "Raw"

    def test_default_raw_with_numbers(self):
        result = extract_card_name("Base Set Charizard 4/102")
        assert result["name"] == "Base Set Charizard 4/102"
        assert result["condition"] == "Raw"

    # Name normalization tests
    def test_name_whitespace_normalization(self):
        result = extract_card_name("pikachu    NM")
        assert result["name"] == "Pikachu"

    def test_name_with_multiple_spaces_between_words(self):
        result = extract_card_name("base  set   charizard  psa 10")
        assert result["name"] == "Base Set Charizard"
        assert result["condition"] == "PSA 10"

    # Priority tests (graded should take precedence over ungraded)
    def test_graded_takes_priority_over_ungraded(self):
        result = extract_card_name("Venusaur PSA 8 NM")
        assert result["condition"] == "PSA 8"

    # Edge cases
    def test_empty_string(self):
        result = extract_card_name("")
        assert result["name"] == ""
        assert result["condition"] == "Raw"

    def test_only_condition_psa(self):
        result = extract_card_name("PSA 10")
        assert result["name"] == ""
        assert result["condition"] == "PSA 10"

    def test_only_condition_nm(self):
        result = extract_card_name("NM")
        assert result["name"] == ""
        assert result["condition"] == "NM"

    def test_decimal_grade(self):
        result = extract_card_name("Lugia BGS 8.5")
        assert result["name"] == "Lugia"
        assert result["condition"] == "BGS 8.5"

    def test_special_characters_in_name(self):
        result = extract_card_name("Articuno-Ex PSA 9")
        assert result["name"] == "Articuno-Ex"
        assert result["condition"] == "PSA 9"

    def test_name_with_parentheses(self):
        result = extract_card_name("Lugia (Secret) NM")
        assert result["name"] == "Lugia (Secret)"
        assert result["condition"] == "NM"

    def test_condition_at_beginning(self):
        result = extract_card_name("NM Charizard")
        assert result["name"] == "Charizard"
        assert result["condition"] == "NM"

    def test_condition_in_middle(self):
        result = extract_card_name("Charizard PSA 10 Secret Rare")
        assert result["name"] == "Charizard Secret Rare"
        assert result["condition"] == "PSA 10"

    def test_multiple_grades_input(self):
        result = extract_card_name("Charizard PSA 10 BGS 10 CGC 9.5")
        assert result["name"] == "Charizard"
        assert result["condition"] == "PSA 10"
