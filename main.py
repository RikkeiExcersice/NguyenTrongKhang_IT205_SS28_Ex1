from abc import ABC, abstractmethod

# ==============================================================================
# 1. ABSTRACT BASE CLASS: BaseEmployee
# ==============================================================================
class BaseEmployee(ABC):
    # Class attributes áp dụng chung toàn hệ thống
    company_name = "Rikkei Education"
    base_salary_rate = 3000000 

    def __init__(self, emp_code: str, name: str):
        # Validate mã nhân sự ngay khi khởi tạo thông qua static method
        if not self.validate_employee_code(emp_code):
            raise ValueError("Mã nhân sự không hợp lệ! Phải gồm đúng 10 ký tự và bắt đầu bằng RKE.")
        
        self._emp_code = emp_code
        self._name = self._normalize_name(name)
        # Thuộc tính private đóng gói số giờ làm việc, chặn sửa đổi trực tiếp từ bên ngoài
        self.__working_hours = 0.0

    # @property: Getter để đọc dữ liệu private một cách an toàn (Không có setter trực tiếp)
    @property
    def working_hours(self) -> float:
        return self.__working_hours

    # Hàm hỗ trợ tăng giờ làm việc một cách nội bộ/hợp lệ
    def _add_working_hours(self, hours: float):
        if hours <= 0:
            raise ValueError("Số giờ làm việc cộng thêm không được nhỏ hơn hoặc bằng 0.")
        self.__working_hours += hours

    @property
    def emp_code(self) -> str:
        return self._emp_code

    @property
    def name(self) -> str:
        return self._name

    # Setter gián tiếp qua việc chuẩn hóa tên nhân sự
    def _normalize_name(self, name: str) -> str:
        return " ".join(name.strip().upper().split())

    # @abstractmethod: Ép buộc các lớp con phải triển khai thuật toán tính lương riêng biệt
    @abstractmethod
    def calculate_salary(self) -> float:
        pass

    # @abstractmethod: Ép buộc các lớp con phải triển khai logic cập nhật hiệu suất riêng biệt
    @abstractmethod
    def update_kpi(self, progress: float):
        pass

    # @staticmethod: Hàm độc lập phục vụ việc kiểm tra tính hợp lệ của mã định danh
    @staticmethod
    def validate_employee_code(emp_code: str) -> bool:
        return len(emp_code) == 10 and emp_code.startswith("RKE")

    # @classmethod: Cho phép thay đổi mức lương cơ sở trên toàn bộ hệ thống
    @classmethod
    def update_base_salary_rate(cls, new_rate: float):
        if new_rate <= 0:
            raise ValueError("Mức lương cơ sở mới phải lớn hơn 0.")
        cls.base_salary_rate = new_rate

    # OPERATOR OVERLOADING
    # Nạp chồng toán tử cộng (+): Cộng dồn giờ làm việc của 2 nhân sự kế thừa từ BaseEmployee
    def __add__(self, other):
        if not isinstance(other, BaseEmployee):
            return NotImplemented
        return self.working_hours + other.working_hours

    # Nạp chồng toán tử so sánh (<): So sánh hiệu suất giờ công giữa 2 nhân sự
    def __lt__(self, other):
        if not isinstance(other, BaseEmployee):
            return NotImplemented
        return self.working_hours < other.working_hours


# ==============================================================================
# 2. SUBCLASSES TRIỂN KHAI CHI TIẾT
# ==============================================================================

class Lecturer(BaseEmployee):
    def __init__(self, emp_code: str, name: str):
        super().__init__(emp_code, name)
        self.teaching_slots = 0 # Thuộc tính đặc thù của giảng viên

    def calculate_salary(self) -> float:
        # Lương = (Giờ làm * Lương cơ sở) + (Số ca dạy * 500,000)
        return (self.working_hours * self.base_salary_rate) + (self.teaching_slots * 500000)

    def update_kpi(self, progress: float):
        # Đối với Lecturer, progress đại diện cho số ca dạy được cộng thêm trực tiếp
        if progress <= 0:
            raise ValueError("Số liệu cập nhật hiệu suất không được nhỏ hơn hoặc bằng 0.")
        self.teaching_slots += int(progress)

    def conduct_class(self):
        """Tự động tăng 1 ca dạy và cộng thêm 2 giờ làm việc"""
        self.teaching_slots += 1
        self._add_working_hours(2.0)


class AdmissionStaff(BaseEmployee):
    def __init__(self, emp_code: str, name: str, kpi_target: float = 100000000.0):
        super().__init__(emp_code, name)
        self.revenue_generated = 0.0 # Doanh số tích lũy mang về
        self.kpi_target = kpi_target

    def calculate_salary(self) -> float:
        # Lương = (Giờ làm * Lương cơ sở) + 5% Hoa hồng doanh số
        return (self.working_hours * self.base_salary_rate) + (self.revenue_generated * 0.05)

    def update_kpi(self, progress: float):
        # Đối với AdmissionStaff, progress đại diện cho doanh số hợp đồng mới mang về
        if progress <= 0:
            raise ValueError("Số liệu cập nhật hiệu suất không được nhỏ hơn hoặc bằng 0.")
        self.revenue_generated += progress


# ==============================================================================
# 3. MULTIPLE INHERITANCE: HybridManager (Đa kế thừa & MRO)
# ==============================================================================
class HybridManager(Lecturer, AdmissionStaff):
    def __init__(self, emp_code: str, name: str):
        # Khởi tạo thông qua super() tuân theo cấu trúc MRO một cách tự động
        super().__init__(emp_code, name)
        # Đồng bộ hóa các thuộc tính đặc thù từ cả 2 nhánh cha
        AdmissionStaff.__init__(self, emp_code, name)

    def calculate_salary(self) -> float:
        # Tích hợp cả cơ chế phụ cấp ca dạy của Lecturer và hoa hồng của AdmissionStaff
        base_and_slots = Lecturer.calculate_salary(self)
        commission = self.revenue_generated * 0.05
        return base_and_slots + commission

    def update_kpi(self, progress: float):
        # Mặc định của Hybrid khi cập nhật KPI chung qua menu sẽ ưu tiên cộng doanh số
        AdmissionStaff.update_kpi(self, progress)


# ==============================================================================
# 4. DUCK TYPING GATEWAY FOR PAYROLL
# ==============================================================================
class VietcombankCorporateService:
    def transfer_salary(self, employee: BaseEmployee, amount: float):
        print("[Hệ thống VCB Corporate]: Đang kết nối tới cổng chi trả Rikkei...")
        print("Xác thực đối tác bằng Duck Typing thành công!")
        print(f"Ngân hàng đối tác đã giải ngân thành công số tiền: {amount:,.0f} VND tới nhân sự {employee.emp_code}.")

class TechcombankCorporateService:
    def transfer_salary(self, employee: BaseEmployee, amount: float):
        print("[Hệ thống Techcombank Business]: Đang thiết lập kết nối API bảo mật...")
        print("Xác thực cổng thanh toán Duck Typing thành công!")
        print(f"Hệ thống TCB đã chuyển khoản thành công {amount:,.0f} VND tới tài khoản nhân sự {employee.emp_code}.")

def execute_payroll(payment_service, employee: BaseEmployee, amount: float):
    """
    Hàm toàn cục áp dụng Duck Typing. Không quan tâm class của payment_service,
    chỉ cần đối tượng đó thực thi được phương thức 'transfer_salary'.
    """
    if not hasattr(payment_service, "transfer_salary") or not callable(getattr(payment_service, "transfer_salary")):
        raise AttributeError("Cổng dịch vụ ngân hàng doanh nghiệp không hợp lệ hoặc chưa được liên kết liên thông kỹ thuật.")
    payment_service.transfer_salary(employee, amount)


# ==============================================================================
# 5. CLI MENU INTERFACE SYSTEM
# ==============================================================================
def main():
    employees = []
    current_employee = None

    # Tạo sẵn một vài nhân sự mẫu để dễ kiểm tra chức năng số 5
    try:
        sample_staff = AdmissionStaff("RKE0099999", "Nguyen Van An")
        sample_staff._add_working_hours(180.0)
        employees.append(sample_staff)
    except Exception:
        pass

    while True:
        print("\n===== RIKKEI EDUCATION HR SIMULATOR PRO =====")
        print("1. Tuyển dụng nhân sự mới (Chọn loại hợp đồng nhân sự)")
        print("2. Xem thông tin & Kiểm tra thứ tự kế thừa (MRO)")
        print("3. Ghi nhận công nhật & Cập nhật KPI (Tính đa hình)")
        print("4. Tổng hợp quỹ lương và ngân sách chi trả")
        print("5. Kiểm tra gộp giờ làm việc & So sánh hiệu suất (Overloading)")
        print("6. Giải ngân lương qua Cổng thanh toán đối tác (Duck Typing)")
        print("7. Thoát chương trình")
        print("==============================================")
        
        choice = input("Chọn chức năng (1-7): ").strip()
        
        if choice == "1":
            print("\n--- CHỌN LOẠI NHÂN SỰ KHỞI TẠO ---")
            print("1. Lecturer (Giảng viên chuyên trách)")
            print("2. Admission Staff (Nhân viên Tuyển sinh)")
            print("3. Hybrid Manager (Quản lý kiêm Giảng dạy)")
            
            type_choice = input("Chọn loại nhân sự (1-3): ").strip()
            emp_code = input("Nhập mã nhân sự 10 ký tự: ").strip()
            name = input("Nhập họ và tên: ").strip()
            
            try:
                if type_choice == "1":
                    new_emp = Lecturer(emp_code, name)
                    msg = "Tuyển dụng Giảng viên thành công!"
                elif type_choice == "2":
                    new_emp = AdmissionStaff(emp_code, name)
                    msg = "Tuyển dụng Nhân viên Tuyển sinh thành công!"
                elif type_choice == "3":
                    new_emp = HybridManager(emp_code, name)
                    msg = "Tuyển dụng Quản lý Hybrid thành công!"
                else:
                    print("Lựa chọn loại nhân sự không hợp lệ!")
                    continue
                
                # Giả định cấp công công nhật ban đầu cho nhân viên mới để chạy test
                new_emp._add_working_hours(160.0)
                if isinstance(new_emp, Lecturer):
                    new_emp.update_kpi(20) # Thêm 20 ca dạy mẫu ban đầu
                if isinstance(new_emp, AdmissionStaff):
                    new_emp.update_kpi(50000000) # Doanh số mẫu 50M
                
                employees.append(new_emp)
                current_employee = new_emp
                print(f"{msg}\nTên nhân sự: {current_employee.name}")
                
            except ValueError as e:
                print(f"Mã nhân sự không hợp lệ! {e}")
                
        elif choice == "2":
            if not current_employee:
                print("Chưa có nhân sự nào active trong hệ thống. Vui lòng tuyển dụng trước!")
                continue
            
            print("\n--- THÔNG TIN NHÂN SỰ HIỆN TẠI ---")
            print(f"Loại nhân sự: {current_employee.__class__.__name__}")
            print(f"Tổ chức: {current_employee.company_name}")
            print(f"Mã nhân sự: {current_employee.emp_code}")
            print(f"Họ và tên: {current_employee.name}")
            print(f"Số giờ làm việc: {current_employee.working_hours:.0f} giờ")
            
            if isinstance(current_employee, Lecturer):
                print(f"Số ca đã dạy: {current_employee.teaching_slots} ca")
            if isinstance(current_employee, AdmissionStaff):
                print(f"Doanh số mang về: {current_employee.revenue_generated:,.0f} VND")
                
            print(f"Thứ tự kế thừa MRO kỹ thuật: {[cls.__name__ for cls in current_employee.__class__.__mro__]}")

        elif choice == "3":
            if not current_employee:
                print("Chưa có nhân sự active để ghi nhận công hiệu suất.")
                continue
            
            print("\n--- GHI NHẬN CÔNG NHẬT & HIỆU SUẤT ---")
            print("1. Ghi nhận tham gia đứng lớp (Chỉ dành cho Giảng viên/Hybrid)")
            print("2. Cập nhật tiến độ KPI / Doanh số")
            task_choice = input("Chọn tác vụ (1-2): ").strip()
            
            try:
                if task_choice == "1":
                    if isinstance(current_employee, Lecturer):
                        current_employee.conduct_class()
                        print("Ghi nhận thành công! Thầy/Cô đã hoàn thành thêm 1 ca dạy.")
                        print(f"Số ca dạy hiện tại: {current_employee.teaching_slots} ca.")
                        print(f"Số giờ làm việc tích lũy: {current_employee.working_hours:.0f} giờ.")
                    else:
                        print("Thất bại: Nhân sự hiện tại không có chức năng giảng dạy!")
                elif task_choice == "2":
                    val = float(input("Nhập giá trị doanh số hợp đồng mới mang về (hoặc số ca dạy thêm nếu là Giảng viên đơn thuần): ").strip())
                    current_employee.update_kpi(val)
                    print("\nCập nhật KPI thành công!")
                    if isinstance(current_employee, AdmissionStaff):
                        print(f"Doanh số tích lũy mới: {current_employee.revenue_generated:,.0f} VND.")
                    else:
                        print(f"Số ca dạy tích lũy mới: {current_employee.teaching_slots} ca.")
            except ValueError as e:
                print(f"[LỖI EDGE CASE 2]: {e}")

        elif choice == "4":
            if not current_employee:
                print("Không có nhân sự active để tính toán lương.")
                continue
            
            print("\n--- CHI TIẾT QUỸ LƯƠNG NHÂN SỰ ---")
            print(f"Nhân sự: {current_employee.name} (Loại: {current_employee.__class__.__name__})")
            print(f"Mức lương cơ sở hệ thống: {current_employee.base_salary_rate:,.0f} VND")
            print(f"Số giờ làm việc tích lũy: {current_employee.working_hours:.0f} giờ")
            
            fixed_salary = current_employee.working_hours * current_employee.base_salary_rate
            total_salary = current_employee.calculate_salary()
            allowance = total_salary - fixed_salary
            
            print(f"Lương cứng tính theo giờ: {fixed_salary:,.0f} VND")
            print(f"Phụ cấp ca dạy + Hoa hồng tuyển sinh tích hợp: {allowance:,.0f} VND")
            print(f"Tổng lương thực nhận tháng này: {total_salary:,.0f} VND")

        elif choice == "5":
            if not current_employee:
                print("Yêu cầu nhân sự active để thực hiện Overloading.")
                continue
            
            print("\n--- ĐỒNG BỘ & SO SÁNH GIỜ CÔNG (OPERATOR OVERLOADING) ---")
            print(f"Nhân sự hiện tại (A): {current_employee.name} (Giờ công: {current_employee.working_hours:.0f} giờ)")
            print("Danh sách mã nhân sự đối ứng hiện có trong hệ thống:")
            for emp in employees:
                if emp.emp_code != current_employee.emp_code:
                    print(f" -> Code: {emp.emp_code} ({emp.name} - Giờ công: {emp.working_hours:.0f} giờ)")
            
            target_code = input("Chọn nhân sự đối ứng (B) từ danh sách: ").strip()
            target_emp = next((e for e in employees if e.emp_code == target_code), None)
            
            # Kiểm tra bẫy Overloading (Edge Case 3) với kiểu dữ liệu lạ
            test_fake = input("Bạn có muốn cố tình test lỗi gộp dữ liệu bằng chuỗi text lạ không? (y/n): ").strip().lower()
            
            try:
                if test_fake == 'y':
                    # Cố tình cộng một Object không phải kế thừa BaseEmployee để kích hoạt ngoại lệ
                    print("[Thử nghiệm]: Thực hiện phép cộng giữa Nhân sự và một Chuỗi String...")
                    result = current_employee + "Chuỗi dữ liệu giả mạo"
                    if result == NotImplemented:
                        raise TypeError("Phép toán không được hỗ trợ cho kiểu dữ liệu này.")
                else:
                    if not target_emp:
                        print("Không tìm thấy nhân sự đối ứng phù hợp!")
                        continue
                    
                    is_less = current_employee < target_emp
                    comp_str = "ÍT HƠN" if is_less else "KHÔNG ÍT HƠN"
                    total_hours = current_employee + target_emp
                    
                    print(f"[Kết quả So sánh (__lt__)]: Giờ công cống hiến của nhân sự A {comp_str} nhân sự B.")
                    print(f"[Kết quả Tổng hợp (__add__)]: Tổng số giờ làm việc của cả 2 nhân sự là: {total_hours:.0f} giờ.")
            except TypeError as e:
                print(f"[LỖI EDGE CASE 3]: Xử lý ngoại lệ thành công! {e}")

        elif choice == "6":
            if not current_employee:
                print("Không có nhân sự nào để lập lệnh giải ngân.")
                continue
                
            print("\n--- CHI TRẢ LƯƠNG QUA CỔNG ĐỐI TÁC TRUNG GIAN ---")
            print("1. Chi trả qua tài khoản Doanh nghiệp Vietcombank")
            print("2. Chi trả qua tài khoản Doanh nghiệp Techcombank")
            print("3. Thử nghiệm cổng lỗi (Bẫy lỗi kỹ thuật Duck Typing)")
            
            bank_choice = input("Chọn cổng ngân hàng (1-3): ").strip()
            amount = current_employee.calculate_salary()
            
            # Khởi tạo đối tượng bank dựa vào lựa chọn
            if bank_choice == "1":
                service = VietcombankCorporateService()
            elif bank_choice == "2":
                service = TechcombankCorporateService()
            elif bank_choice == "3":
                # Một Class lỗi không thiết kế hàm transfer_salary
                class InvalidBankService: pass
                service = InvalidBankService()
            else:
                print("Lựa chọn không hợp lệ.")
                continue
                
            try:
                execute_payroll(service, current_employee, amount)
            except AttributeError as e:
                print(f"[LỖI EDGE CASE 4]: {e}")

        elif choice == "7":
            print("Cảm ơn đã sử dụng hệ thống Quản lý Nhân sự Rikkei Education Pro!")
            break
        else:
            print("Lựa chọn không chính xác. Vui lòng nhập từ 1 đến 7.")

# Thử nghiệm Bẫy lỗi Khởi tạo trực tiếp Abstract Class (Edge Case 1)
try:
    print("[Hệ thống Kiểm Tra Đóng Gói]: Thử khởi tạo trực tiếp BaseEmployee...")
    failed_emp = BaseEmployee("RKE1111111", "Trần Văn Lỗi")
except TypeError as e:
    print(f"[LỖI EDGE CASE 1]: Chặn khởi tạo trực tiếp Abstract Base Class thành công! Chi tiết lỗi: {e}\n")

if __name__ == "__main__":
    main()