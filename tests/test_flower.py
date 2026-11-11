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
        assert species in flower.species_names, f"Expected known species. Instead unknown species: {species}"
        assert style in flower.art_styles, f"Expected known art style. Instead unknown art style: {style}" 
        assert flower.choose_flower(hash_test) == (species, style), "Exptected same species & style from same hash"

    def test_choose_flower_uses_correct_bytes(self):
        """
        Verify choose_flower() that byte 0 of hash picks species and byte 4 picks art style
        """
        # every byte is 00, both pick first item in their list
        species, style = flower.choose_flower("00" * 32)
        assert species == flower.species_names[0], f"Expected to pick first species in list, instead: {species}"
        assert style == flower.art_styles[0], f"Expected to pick first art style in list, instead: {style}" 

    def test_choose_flower_requires_a_sha256_hash(self):
        """
        Verify choose_flower() raise error for not a sha-256 hash
        """
        with pytest.raises(ValueError):
            flower.choose_flower("00")
        with pytest.raises(ValueError):
            flower.choose_flower("not hex")

    def test_render_flower_svg_valid(self):
        """
        Verify render_flower_svg() returns a svg 
        """
        svg = flower.render_flower_svg(hash_test)
        assert svg.startswith("<svg"), "Expected the text to start with <svg"
        assert svg.endswith("</svg>"), "Expected the text to end with </svg>"
        assert "title>" in svg, "Expected the svg to have title to know flower and art style"

    def test_render_flower_svg_different(self):
        """
        Verify render_flower_svg() return different pictures for different hashes
        """
        image1 = flower.render_flower_svg("00" * 32)
        image2 = flower.render_flower_svg("ac" * 32)

        assert image1 != image2, "Expected different images for different hashes"

    def test_render_flower_svg_invalid(self):
        """
        Verify render_flower_svg raise error for not a sha-256 hash
        """
        with pytest.raises(ValueError):
            flower.render_flower_svg("00")
        with pytest.raises(ValueError):
            flower.render_flower_svg("not hex")

    def test_svg_to_file_valid(self, tmp_path):
        """
        Verify svg_to_file() returns a valide .svg file
        """
        output = tmp_path / "my_flower.svg"
        flower.svg_to_file(hash_test, output)

        assert output.exists(), "Expected .svg file, but does not exist"
        assert output.name == "my_flower.svg", "Expected correct filename"
        assert output.read_text(encoding="utf-8").startswith("<svg"), "Expected .svg file to hold svg text"