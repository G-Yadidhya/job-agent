from src.url_builder import NaukriURLBuilder, RemoteOKURLBuilder, WellfoundURLBuilder


class TestNaukriURLBuilder:
    def test_naukri_url_with_title_and_location(self):
        url = NaukriURLBuilder.build_search_url("Product Manager", "bangalore")
        assert url == "https://www.naukri.com/product-manager-jobs-in-bangalore-city"

    def test_naukri_url_with_title_and_mumbai(self):
        url = NaukriURLBuilder.build_search_url("Software Engineer", "mumbai")
        assert url == "https://www.naukri.com/software-engineer-jobs-in-mumbai-city"

    def test_naukri_url_with_title_only(self):
        url = NaukriURLBuilder.build_search_url("Data Scientist", None)
        assert url == "https://www.naukri.com/data-scientist-jobs"

    def test_naukri_url_remote_location(self):
        url = NaukriURLBuilder.build_search_url("Backend Engineer", "remote")
        assert url == "https://www.naukri.com/backend-engineer-jobs"

    def test_naukri_url_with_spaces_in_title(self):
        url = NaukriURLBuilder.build_search_url("Senior Software Engineer", "pune")
        assert url == "https://www.naukri.com/senior-software-engineer-jobs-in-pune-city"

    def test_naukri_url_empty_title(self):
        url = NaukriURLBuilder.build_search_url("", "bangalore")
        assert url == "https://www.naukri.com"

    def test_naukri_url_none_title(self):
        url = NaukriURLBuilder.build_search_url(None, None)
        assert url == "https://www.naukri.com"


class TestRemoteOKURLBuilder:
    def test_remoteok_url_with_title(self):
        url = RemoteOKURLBuilder.build_search_url("Product Manager", "bangalore")
        assert url == "https://remoteok.io?q=Product%20Manager"

    def test_remoteok_url_with_special_chars(self):
        url = RemoteOKURLBuilder.build_search_url("C++ Developer", None)
        assert "remoteok.io" in url
        assert "q=C" in url

    def test_remoteok_url_empty_title(self):
        url = RemoteOKURLBuilder.build_search_url("", None)
        assert url == "https://remoteok.io"


class TestWellfoundURLBuilder:
    def test_wellfound_url_with_title(self):
        url = WellfoundURLBuilder.build_search_url("Product Manager", None)
        assert url == "https://wellfound.com/jobs?query=Product%20Manager"

    def test_wellfound_url_with_title_and_location(self):
        url = WellfoundURLBuilder.build_search_url("Software Engineer", "bangalore")
        assert "wellfound.com/jobs" in url
        assert "query=Software%20Engineer" in url
        assert "location=bangalore" in url

    def test_wellfound_url_empty_title(self):
        url = WellfoundURLBuilder.build_search_url("", None)
        assert url == "https://wellfound.com/jobs"
