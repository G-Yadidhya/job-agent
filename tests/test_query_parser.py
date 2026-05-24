from src.query_parser import QueryParser


def test_query_parser_extracts_title_and_location():
    result = QueryParser.parse("Find Product Manager roles in bangalore")
    assert result["title"] == "Product Manager"
    assert result["location"] == "bangalore"


def test_query_parser_extracts_remote_location():
    result = QueryParser.parse("Software Engineer jobs in remote")
    assert result["title"] == "Software Engineer"
    assert result["location"] == "remote"


def test_query_parser_handles_alternate_locations():
    result = QueryParser.parse("Data Scientist positions in pune")
    assert result["title"] == "Data Scientist"
    assert result["location"] == "pune"


def test_query_parser_handles_title_without_location():
    result = QueryParser.parse("Software Engineer")
    assert result["title"] == "Software Engineer"
    assert result["location"] is None


def test_query_parser_handles_bengaluru_alias():
    result = QueryParser.parse("Find Backend Engineer roles in bengaluru")
    assert result["title"] == "Backend Engineer"
    assert result["location"] == "bangalore"


def test_query_parser_handles_wfh_alias():
    result = QueryParser.parse("Product Manager jobs in wfh")
    assert result["title"] == "Product Manager"
    assert result["location"] == "remote"


def test_query_parser_extracts_from_complex_query():
    result = QueryParser.parse("Looking for Senior Software Engineer positions in mumbai and bangalore")
    # Should match "Software Engineer" from common titles
    assert "Software Engineer" in result["title"]
    # Should match the first location found
    assert result["location"] in ["mumbai", "bangalore"]


def test_query_parser_handles_empty_query():
    result = QueryParser.parse("")
    assert result["title"] is None
    assert result["location"] is None


def test_query_parser_case_insensitive():
    result = QueryParser.parse("FIND PRODUCT MANAGER ROLES IN BANGALORE")
    assert result["title"] == "Product Manager"
    assert result["location"] == "bangalore"


def test_query_parser_handles_no_recognized_title():
    result = QueryParser.parse("in mumbai looking for xyz role")
    # Should still extract location
    assert result["location"] == "mumbai"
    # Title might be None or the remaining text
    assert result["title"] is None or "Xyz Role" in result["title"]
