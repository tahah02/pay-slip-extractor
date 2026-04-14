import pytest
from extractors.payslip_extractor import PayslipExtractor
from utils.text_cleaner import TextCleaner


@pytest.fixture
def extractor():
    return PayslipExtractor()


@pytest.fixture
def cleaner():
    return TextCleaner()


class TestNameExtraction:
    def test_extract_name_with_nama_keyword(self, extractor):
        text = "Nama: Moody bin Pitah"
        result = extractor.extract_payslip_fields(text)
        assert result['name'] == "Moody bin Pitah"
    
    def test_extract_name_with_employee_keyword(self, extractor):
        text = "Employee Name: John Doe"
        result = extractor.extract_payslip_fields(text)
        assert result['name'] == "John Doe"
    
    def test_extract_name_uppercase(self, extractor):
        text = "NAMA PEKERJA: AHMAD BIN HASSAN"
        result = extractor.extract_payslip_fields(text)
        assert result['name'] is not None


class TestIDNumberExtraction:
    def test_extract_id_with_no_kp_keyword(self, extractor):
        text = "No. K/P: 780809-12-5503"
        result = extractor.extract_payslip_fields(text)
        assert result['id_number'] == "780809-12-5503"
    
    def test_extract_id_with_no_ic_keyword(self, extractor):
        text = "No. IC: 123456-12-1234"
        result = extractor.extract_payslip_fields(text)
        assert result['id_number'] == "123456-12-1234"
    
    def test_extract_id_12_digit_format(self, extractor):
        text = "NRIC: 780809125503"
        result = extractor.extract_payslip_fields(text)
        assert result['id_number'] is not None


class TestGrossIncomeExtraction:
    def test_extract_gross_with_jumlah_pendapatan(self, extractor):
        text = "Jumlah Pendapatan: RM 40000.00"
        result = extractor.extract_payslip_fields(text)
        assert result['gross_income'] == "40000.00"
    
    def test_extract_gross_with_gaji_kasar(self, extractor):
        text = "Gaji Kasar: 50000.00"
        result = extractor.extract_payslip_fields(text)
        assert result['gross_income'] == "50000.00"
    
    def test_extract_gross_with_comma_separator(self, extractor):
        text = "Gross Income: RM 40,000.00"
        result = extractor.extract_payslip_fields(text)
        assert result['gross_income'] == "40000.00"


class TestNetIncomeExtraction:
    def test_extract_net_with_gaji_bersih(self, extractor):
        text = "Gaji Bersih: RM 30601.00"
        result = extractor.extract_payslip_fields(text)
        assert result['net_income'] == "30601.00"
    
    def test_extract_net_with_take_home(self, extractor):
        text = "Take Home: 35000.00"
        result = extractor.extract_payslip_fields(text)
        assert result['net_income'] == "35000.00"
    
    def test_calculate_net_from_gross_and_deduction(self, extractor):
        text = """
        Jumlah Pendapatan: 40000.00
        Jumlah Potongan: 9399.00
        """
        result = extractor.extract_payslip_fields(text)
        assert result['net_income'] == "30601.00"


class TestDeductionExtraction:
    def test_extract_deduction_with_jumlah_potongan(self, extractor):
        text = "Jumlah Potongan: RM 9399.00"
        result = extractor.extract_payslip_fields(text)
        assert result['total_deduction'] == "9399.00"
    
    def test_extract_deduction_with_total_deduction(self, extractor):
        text = "Total Deduction: 5000.00"
        result = extractor.extract_payslip_fields(text)
        assert result['total_deduction'] == "5000.00"
    
    def test_calculate_deduction_from_items(self, extractor):
        text = """
        EPF: 1000.00
        SOCSO: 500.00
        Income Tax: 2000.00
        """
        result = extractor.extract_payslip_fields(text)
        assert result['total_deduction'] == "3500.00"


class TestMonthYearExtraction:
    def test_extract_month_year_mm_yyyy_format(self, extractor):
        text = "Bulan: 10/2025"
        result = extractor.extract_payslip_fields(text)
        assert result['month_year'] == "10/2025"
    
    def test_extract_month_year_with_period_keyword(self, extractor):
        text = "Period: 12/2024"
        result = extractor.extract_payslip_fields(text)
        assert result['month_year'] == "12/2024"


class TestConfidenceScore:
    def test_confidence_all_fields_present(self, extractor):
        text = """
        Nama: John Doe
        No. K/P: 123456-12-1234
        Jumlah Pendapatan: 40000.00
        Gaji Bersih: 30601.00
        Jumlah Potongan: 9399.00
        Bulan: 10/2025
        """
        result = extractor.extract_payslip_fields(text)
        confidence = extractor.calculate_confidence(result)
        assert confidence == 1.0
    
    def test_confidence_partial_fields(self, extractor):
        text = """
        Nama: John Doe
        No. K/P: 123456-12-1234
        Jumlah Pendapatan: 40000.00
        """
        result = extractor.extract_payslip_fields(text)
        confidence = extractor.calculate_confidence(result)
        assert 0 < confidence < 1.0


class TestValidation:
    def test_validate_negative_gross_income(self, extractor):
        text = "Jumlah Pendapatan: -40000.00"
        result = extractor.extract_payslip_fields(text)
        assert 'validation_errors' in result
    
    def test_validate_invalid_month(self, extractor):
        text = "Bulan: 13/2025"
        result = extractor.extract_payslip_fields(text)
        assert 'validation_errors' in result
    
    def test_validate_math_mismatch(self, extractor):
        text = """
        Jumlah Pendapatan: 40000.00
        Gaji Bersih: 25000.00
        Jumlah Potongan: 9399.00
        """
        result = extractor.extract_payslip_fields(text)
        assert 'validation_errors' in result


class TestOCRErrorCorrection:
    def test_correct_ocr_letter_o_to_zero(self, cleaner):
        text = "No. K/P: 78O8O9-12-55O3"
        cleaned = cleaner.clean_text(text)
        assert "780809" in cleaned or "O" not in cleaned
    
    def test_correct_ocr_letter_l_to_one(self, cleaner):
        text = "Amount: 5000.l0"
        cleaned = cleaner.clean_text(text)
        assert "5000.10" in cleaned or "l" not in cleaned


class TestTextCleaning:
    def test_clean_extra_spaces(self, cleaner):
        text = "Nama:    John    Doe"
        cleaned = cleaner.clean_text(text)
        assert "  " not in cleaned
    
    def test_normalize_currency(self, cleaner):
        value = "RM 40,000.00"
        normalized = cleaner.normalize_currency(value)
        assert normalized == "40000.00"
    
    def test_normalize_id_number(self, cleaner):
        value = "780809125503"
        normalized = cleaner.normalize_id_number(value)
        assert normalized == "780809-12-5503"
    
    def test_normalize_date(self, cleaner):
        value = "10/2025"
        normalized = cleaner.normalize_date(value)
        assert normalized == "10/2025"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
