import hashlib
import pytest
import pynesthesia.flower as flower

hash_test = hashlib.sha256(b"helloworld").hexdigest()

class Tests:
    def test_choose_flower_valid(self):
        """
        Verify choose_flower() returns a known species and art style.
        """
        species, style = flower.choose_flower(hash_test)
        assert species in flower.species_names, f"Expected known species. Instead unknown specie: {species}"
        assert style in flower.art_styles, f"Expected known art style. Instead unknown art style: {style}" 
        assert flower.choose_flower(hash_test) == (species, style), "Exptected same species & style from same hash"
    
    def test_choose_flower_uses_correct_bytes(self):
        """
        Verify choose_flower() that byte 0 of hash picks species and byte 4 picks art style
        """
        #every byte is 00, both pick first item in their list
        species, style = flower.choose_flower("00" * 32)
        assert species == flower.species_names[0], "Expected to pick first species in list, instead: {species}"
        assert style == flower.art_styles[0], "Expected to picl firt art style in list, instead: {style}" 

    def test_choose_flower_is_invalid(self):
        """
        Verify choose_flower() that byte 0 of hash picks species and byte 4 picks art style
        """
        #every byte is 00, both pick first item in their list
        species, style = flower.choose_flower("00" * 32)
        assert species == flower.species_names[0], "Expected to pick first species in list, instead: {species}"
        assert style == flower.art_styles[0], "Expected to picl firt art style in list, instead: {style}" 
                
    def test_choose_flower_requires_a_sha256_hash(self):
        """
        Verify choose_flower() raise error for not a sha-256 hash
        """
        with pytest.raises(ValueError):
            flower.choose_flower("00")
        with pytest.raises(ValueError):
            flower.choose_flower("not hex")
