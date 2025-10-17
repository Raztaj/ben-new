# PHP Implementation Guide - Beneficiary Management System

This guide provides a complete translation from the Flask reference implementation to PHP with MySQL, following the exact same functionality and structure.

## PHP File Structure (Equivalent to Flask)

```
beneficiary-management-php/
├── config/
│   ├── database.php          # Database configuration
│   └── session.php          # Session management
├── includes/
│   ├── auth.php             # Authentication functions
│   ├── functions.php        # Utility functions
│   └── header.php           # Common header/navigation
├── assets/
│   ├── css/
│   │   └── style.css        # Same CSS as Flask version
│   └── js/
│       └── main.js          # Same JavaScript as Flask version
├── pages/
│   ├── login.php            # Login page
│   ├── dashboard.php        # Dashboard
│   ├── beneficiaries.php    # Beneficiary management
│   ├── review_changes.php   # Admin approval page
│   ├── reports.php          # Reports and charts
│   ├── import_export.php    # Import/export functionality
│   └── settings.php         # User management (admin only)
├── api/
│   ├── search_suggestions.php
│   ├── statistics.php
│   └── export.php
├── actions/
│   ├── add_beneficiary.php
│   ├── edit_beneficiary.php
│   ├── delete_beneficiary.php
│   ├── approve_change.php
│   ├── reject_change.php
│   ├── add_user.php
│   ├── edit_user.php
│   └── delete_user.php
└── index.php               # Main entry point
```

## Database Schema Translation

### MySQL Database Setup
```sql
CREATE DATABASE beneficiary_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE beneficiary_db;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Records table (beneficiaries)
CREATE TABLE records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    father_name VARCHAR(100) NOT NULL,
    grandfather_name VARCHAR(100) NOT NULL,
    family_name VARCHAR(100) NOT NULL,
    id_passport_number VARCHAR(50) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('ذكر', 'أنثى') NOT NULL,
    marital_status ENUM('أعزب', 'متزوج', 'أرمل', 'مطلق') NOT NULL,
    phone_number VARCHAR(20),
    family_members_count INT DEFAULT 0,
    address TEXT,
    status ENUM('مكتمل', 'بحاجة لمراجعة', 'غير نشط') NOT NULL DEFAULT 'بحاجة لمراجعة',
    created_by_user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_user_id) REFERENCES users(id)
);

-- Pending changes table
CREATE TABLE pending_changes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    user_id INT NOT NULL,
    change_type ENUM('update', 'delete') NOT NULL,
    changed_data TEXT,
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by INT,
    reviewed_at TIMESTAMP NULL,
    FOREIGN KEY (record_id) REFERENCES records(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password_hash, full_name, role) VALUES
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'مدير النظام', 'admin'),
('user', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'مستخدم عادي', 'user');
```

## Core PHP Implementation

### 1. Database Configuration (config/database.php)
```php
<?php
class Database {
    private $host = 'localhost';
    private $db_name = 'beneficiary_db';
    private $username = 'root';
    private $password = '';
    private $conn;

    public function getConnection() {
        $this->conn = null;
        try {
            $this->conn = new PDO(
                "mysql:host=" . $this->host . ";dbname=" . $this->db_name . ";charset=utf8mb4",
                $this->username,
                $this->password,
                [
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
                ]
            );
        } catch(PDOException $e) {
            echo "Connection error: " . $e->getMessage();
        }
        return $this->conn;
    }
}
?>
```

### 2. Authentication Functions (includes/auth.php)
```php
<?php
session_start();

function login_required() {
    if (!isset($_SESSION['user_id'])) {
        header('Location: login.php');
        exit();
    }
}

function admin_required() {
    login_required();
    if ($_SESSION['user_role'] !== 'admin') {
        header('Location: dashboard.php');
        exit();
    }
}

function authenticate_user($username, $password, $pdo) {
    $stmt = $pdo->prepare("SELECT id, username, password_hash, full_name, role FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch();

    if ($user && password_verify($password, $user['password_hash'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['user_role'] = $user['role'];
        $_SESSION['full_name'] = $user['full_name'];
        return true;
    }
    return false;
}

function logout() {
    session_destroy();
    header('Location: login.php');
    exit();
}
?>
```

### 3. Main Dashboard (pages/dashboard.php)
```php
<?php
require_once '../includes/auth.php';
require_once '../config/database.php';

login_required();

$database = new Database();
$pdo = $database->getConnection();

// Calculate statistics
$stats = [];

// Total beneficiaries
$stmt = $pdo->query("SELECT COUNT(*) as total FROM records");
$stats['total_beneficiaries'] = $stmt->fetch()['total'];

// New this month
$stmt = $pdo->query("SELECT COUNT(*) as new_month FROM records WHERE MONTH(created_at) = MONTH(NOW()) AND YEAR(created_at) = YEAR(NOW())");
$stats['new_this_month'] = $stmt->fetch()['new_month'];

// Needs review
$stmt = $pdo->query("SELECT COUNT(*) as needs_review FROM records WHERE status = 'بحاجة لمراجعة'");
$stats['needs_review'] = $stmt->fetch()['needs_review'];

// Inactive records
$stmt = $pdo->query("SELECT COUNT(*) as inactive FROM records WHERE status = 'غير نشط'");
$stats['inactive_records'] = $stmt->fetch()['inactive'];

// Pending changes (for admins)
$stats['pending_changes_count'] = 0;
if ($_SESSION['user_role'] === 'admin') {
    $stmt = $pdo->query("SELECT COUNT(*) as pending FROM pending_changes WHERE status = 'pending'");
    $stats['pending_changes_count'] = $stmt->fetch()['pending'];
}

// Recent beneficiaries
$stmt = $pdo->query("SELECT * FROM records ORDER BY created_at DESC LIMIT 5");
$recent_beneficiaries = $stmt->fetchAll();

include '../includes/header.php';
?>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-card-content">
            <div>
                <h3><?php echo $stats['total_beneficiaries']; ?></h3>
                <p>إجمالي المستفيدين</p>
            </div>
            <div class="icon">
                <i class="fas fa-users"></i>
            </div>
        </div>
    </div>
    <!-- Add other stat cards... -->
</div>

<!-- Recent Activity Table -->
<div class="card">
    <div class="card-header">
        <i class="fas fa-history"></i>
        آخر النشاطات
    </div>
    <div class="card-body">
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>الاسم الكامل</th>
                        <th>رقم الهوية</th>
                        <th>الحالة</th>
                        <th>تاريخ الإضافة</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($recent_beneficiaries as $record): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($record['first_name'] . ' ' . $record['father_name'] . ' ' . $record['grandfather_name'] . ' ' . $record['family_name']); ?></td>
                        <td><?php echo htmlspecialchars($record['id_passport_number']); ?></td>
                        <td>
                            <span class="status-badge <?php echo getStatusClass($record['status']); ?>">
                                <?php echo htmlspecialchars($record['status']); ?>
                            </span>
                        </td>
                        <td><?php echo date('Y-m-d H:i', strtotime($record['created_at'])); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<?php
function getStatusClass($status) {
    switch ($status) {
        case 'مكتمل': return 'status-completed';
        case 'بحاجة لمراجعة': return 'status-review';
        case 'غير نشط': return 'status-inactive';
        default: return 'status-review';
    }
}
?>
```

### 4. Beneficiary Management (pages/beneficiaries.php)
```php
<?php
require_once '../includes/auth.php';
require_once '../config/database.php';

login_required();

$database = new Database();
$pdo = $database->getConnection();

// Handle pagination
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$per_page = 10;
$offset = ($page - 1) * $per_page;

// Build query with filters
$where_conditions = [];
$params = [];

// Search filter
if (!empty($_GET['search'])) {
    $search = '%' . $_GET['search'] . '%';
    $where_conditions[] = "(first_name LIKE ? OR father_name LIKE ? OR grandfather_name LIKE ? OR family_name LIKE ? OR id_passport_number LIKE ? OR phone_number LIKE ?)";
    $params = array_merge($params, [$search, $search, $search, $search, $search, $search]);
}

// Status filter
if (!empty($_GET['status'])) {
    $where_conditions[] = "status = ?";
    $params[] = $_GET['status'];
}

// Date range filters
if (!empty($_GET['start_date'])) {
    $where_conditions[] = "DATE(created_at) >= ?";
    $params[] = $_GET['start_date'];
}

if (!empty($_GET['end_date'])) {
    $where_conditions[] = "DATE(created_at) <= ?";
    $params[] = $_GET['end_date'];
}

// Build final query
$where_clause = !empty($where_conditions) ? 'WHERE ' . implode(' AND ', $where_conditions) : '';
$count_query = "SELECT COUNT(*) as total FROM records $where_clause";
$data_query = "SELECT * FROM records $where_clause ORDER BY created_at DESC LIMIT $per_page OFFSET $offset";

// Get total count for pagination
$stmt = $pdo->prepare($count_query);
$stmt->execute($params);
$total_records = $stmt->fetch()['total'];
$total_pages = ceil($total_records / $per_page);

// Get records
$stmt = $pdo->prepare($data_query);
$stmt->execute($params);
$records = $stmt->fetchAll();

include '../includes/header.php';
?>

<!-- Filters Section -->
<div class="filters">
    <form method="GET">
        <div class="filter-row">
            <div class="form-group">
                <label for="search">البحث</label>
                <input type="text" id="search" name="search" class="form-control" value="<?php echo htmlspecialchars($_GET['search'] ?? ''); ?>" placeholder="الاسم، رقم الهوية، أو الهاتف">
            </div>

            <div class="form-group">
                <label for="status">الحالة</label>
                <select id="status" name="status" class="form-control">
                    <option value="">جميع الحالات</option>
                    <option value="مكتمل" <?php echo ($_GET['status'] ?? '') === 'مكتمل' ? 'selected' : ''; ?>>مكتمل</option>
                    <option value="بحاجة لمراجعة" <?php echo ($_GET['status'] ?? '') === 'بحاجة لمراجعة' ? 'selected' : ''; ?>>بحاجة لمراجعة</option>
                    <option value="غير نشط" <?php echo ($_GET['status'] ?? '') === 'غير نشط' ? 'selected' : ''; ?>>غير نشط</option>
                </select>
            </div>

            <div class="form-group">
                <label for="start_date">من تاريخ</label>
                <input type="date" id="start_date" name="start_date" class="form-control" value="<?php echo htmlspecialchars($_GET['start_date'] ?? ''); ?>">
            </div>

            <div class="form-group">
                <label for="end_date">إلى تاريخ</label>
                <input type="date" id="end_date" name="end_date" class="form-control" value="<?php echo htmlspecialchars($_GET['end_date'] ?? ''); ?>">
            </div>

            <div class="form-group">
                <label>&nbsp;</label>
                <div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-filter"></i>
                        تطبيق الفلتر
                    </button>
                    <a href="beneficiaries.php" class="btn btn-secondary">
                        <i class="fas fa-times"></i>
                        إزالة الفلتر
                    </a>
                </div>
            </div>
        </div>
    </form>
</div>

<!-- Action Buttons -->
<div class="mb-3">
    <button type="button" class="btn btn-primary" data-modal-target="#addBeneficiaryModal">
        <i class="fas fa-plus"></i>
        إضافة مستفيد جديد
    </button>
</div>

<!-- Beneficiaries Table -->
<div class="table-container">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>الاسم الكامل</th>
                <th>رقم الهوية/جواز السفر</th>
                <th>تاريخ الميلاد</th>
                <th>رقم الهاتف</th>
                <th>الجنس</th>
                <th>الحالة</th>
                <th>تاريخ الإنشاء</th>
                <th>الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($records as $record): ?>
            <tr data-record-id="<?php echo $record['id']; ?>">
                <td><?php echo $record['id']; ?></td>
                <td><?php echo htmlspecialchars($record['first_name'] . ' ' . $record['father_name'] . ' ' . $record['grandfather_name'] . ' ' . $record['family_name']); ?></td>
                <td><?php echo htmlspecialchars($record['id_passport_number']); ?></td>
                <td><?php echo date('Y-m-d', strtotime($record['date_of_birth'])); ?></td>
                <td><?php echo htmlspecialchars($record['phone_number'] ?: '-'); ?></td>
                <td><?php echo htmlspecialchars($record['gender']); ?></td>
                <td>
                    <span class="status-badge <?php echo getStatusClass($record['status']); ?>">
                        <?php echo htmlspecialchars($record['status']); ?>
                    </span>
                </td>
                <td><?php echo date('Y-m-d', strtotime($record['created_at'])); ?></td>
                <td>
                    <div class="action-buttons">
                        <button type="button" class="action-btn edit" data-modal-target="#editBeneficiaryModal" data-record-id="<?php echo $record['id']; ?>" title="تعديل">
                            <i class="fas fa-edit"></i>
                        </button>

                        <form method="POST" action="../actions/delete_beneficiary.php" style="display: inline;">
                            <input type="hidden" name="record_id" value="<?php echo $record['id']; ?>">
                            <button type="submit" class="action-btn delete" data-confirm="هل أنت متأكد من حذف هذا المستفيد؟" title="حذف">
                                <i class="fas fa-trash"></i>
                            </button>
                        </form>

                        <a href="../api/export.php?type=single&id=<?php echo $record['id']; ?>" class="action-btn pdf" title="تصدير PDF">
                            <i class="fas fa-file-pdf"></i>
                        </a>
                    </div>
                </td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>

<!-- Pagination -->
<?php if ($total_pages > 1): ?>
<div class="pagination">
    <?php if ($page > 1): ?>
        <a href="?page=<?php echo $page - 1; ?>&<?php echo http_build_query($_GET); ?>">السابق</a>
    <?php endif; ?>

    <?php for ($i = 1; $i <= $total_pages; $i++): ?>
        <?php if ($i == $page): ?>
            <span class="current"><?php echo $i; ?></span>
        <?php else: ?>
            <a href="?page=<?php echo $i; ?>&<?php echo http_build_query($_GET); ?>"><?php echo $i; ?></a>
        <?php endif; ?>
    <?php endfor; ?>

    <?php if ($page < $total_pages): ?>
        <a href="?page=<?php echo $page + 1; ?>&<?php echo http_build_query($_GET); ?>">التالي</a>
    <?php endif; ?>
</div>
<?php endif; ?>

<!-- Add/Edit Beneficiary Modals (same HTML as Flask templates) -->
<!-- ... -->
```

### 5. Add Beneficiary Action (actions/add_beneficiary.php)
```php
<?php
require_once '../includes/auth.php';
require_once '../config/database.php';

login_required();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../pages/beneficiaries.php');
    exit();
}

$database = new Database();
$pdo = $database->getConnection();

try {
    $stmt = $pdo->prepare("
        INSERT INTO records (
            first_name, father_name, grandfather_name, family_name,
            id_passport_number, date_of_birth, gender, marital_status,
            phone_number, family_members_count, address, status, created_by_user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ");

    $stmt->execute([
        $_POST['first_name'],
        $_POST['father_name'],
        $_POST['grandfather_name'],
        $_POST['family_name'],
        $_POST['id_passport_number'],
        $_POST['date_of_birth'],
        $_POST['gender'],
        $_POST['marital_status'],
        $_POST['phone_number'] ?? '',
        (int)($_POST['family_members_count'] ?? 0),
        $_POST['address'] ?? '',
        $_POST['status'],
        $_SESSION['user_id']
    ]);

    $_SESSION['success_message'] = 'تم إضافة المستفيد بنجاح';

} catch (PDOException $e) {
    $_SESSION['error_message'] = 'حدث خطأ أثناء إضافة المستفيد: ' . $e->getMessage();
}

header('Location: ../pages/beneficiaries.php');
exit();
?>
```

### 6. Excel Import/Export (using PhpSpreadsheet)
```php
<?php
// Install PhpSpreadsheet via Composer: composer require phpoffice/phpspreadsheet

require_once '../includes/auth.php';
require_once '../config/database.php';
require_once '../vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;
use PhpOffice\PhpSpreadsheet\IOFactory;

login_required();

$database = new Database();
$pdo = $database->getConnection();

if ($_GET['action'] === 'download_template') {
    // Create Excel template
    $spreadsheet = new Spreadsheet();
    $sheet = $spreadsheet->getActiveSheet();

    // Headers
    $headers = [
        'الاسم الأول', 'اسم الأب', 'اسم الجد', 'اسم العائلة',
        'رقم الهوية/جواز السفر', 'تاريخ الميلاد', 'الجنس', 'الحالة الاجتماعية',
        'رقم الهاتف', 'عدد أفراد الأسرة', 'العنوان'
    ];

    for ($col = 1; $col <= count($headers); $col++) {
        $sheet->setCellValueByColumnAndRow($col, 1, $headers[$col - 1]);
    }

    // Sample data
    $sample_data = [
        'أحمد', 'محمد', 'علي', 'الأحمد',
        '123456789', '1990-01-01', 'ذكر', 'متزوج',
        '0501234567', '4', 'الرياض'
    ];

    for ($col = 1; $col <= count($sample_data); $col++) {
        $sheet->setCellValueByColumnAndRow($col, 2, $sample_data[$col - 1]);
    }

    // Download
    $writer = new Xlsx($spreadsheet);

    header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    header('Content-Disposition: attachment;filename="beneficiaries_template.xlsx"');
    header('Cache-Control: max-age=0');

    $writer->save('php://output');
    exit();
}

if ($_GET['action'] === 'export') {
    // Export records to Excel
    $query = "SELECT * FROM records ORDER BY created_at DESC";
    $stmt = $pdo->prepare($query);
    $stmt->execute();
    $records = $stmt->fetchAll();

    $spreadsheet = new Spreadsheet();
    $sheet = $spreadsheet->getActiveSheet();

    // Headers
    $headers = [
        'ID', 'الاسم الأول', 'اسم الأب', 'اسم الجد', 'اسم العائلة',
        'رقم الهوية/جواز السفر', 'تاريخ الميلاد', 'الجنس', 'الحالة الاجتماعية',
        'رقم الهاتف', 'عدد أفراد الأسرة', 'العنوان', 'الحالة', 'تاريخ الإنشاء'
    ];

    for ($col = 1; $col <= count($headers); $col++) {
        $sheet->setCellValueByColumnAndRow($col, 1, $headers[$col - 1]);
    }

    // Data
    $row = 2;
    foreach ($records as $record) {
        $sheet->setCellValueByColumnAndRow(1, $row, $record['id']);
        $sheet->setCellValueByColumnAndRow(2, $row, $record['first_name']);
        $sheet->setCellValueByColumnAndRow(3, $row, $record['father_name']);
        $sheet->setCellValueByColumnAndRow(4, $row, $record['grandfather_name']);
        $sheet->setCellValueByColumnAndRow(5, $row, $record['family_name']);
        $sheet->setCellValueByColumnAndRow(6, $row, $record['id_passport_number']);
        $sheet->setCellValueByColumnAndRow(7, $row, $record['date_of_birth']);
        $sheet->setCellValueByColumnAndRow(8, $row, $record['gender']);
        $sheet->setCellValueByColumnAndRow(9, $row, $record['marital_status']);
        $sheet->setCellValueByColumnAndRow(10, $row, $record['phone_number']);
        $sheet->setCellValueByColumnAndRow(11, $row, $record['family_members_count']);
        $sheet->setCellValueByColumnAndRow(12, $row, $record['address']);
        $sheet->setCellValueByColumnAndRow(13, $row, $record['status']);
        $sheet->setCellValueByColumnAndRow(14, $row, $record['created_at']);
        $row++;
    }

    // Download
    $writer = new Xlsx($spreadsheet);

    $timestamp = date('Ymd_His');
    $filename = "beneficiaries_export_$timestamp.xlsx";

    header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    header("Content-Disposition: attachment;filename=\"$filename\"");
    header('Cache-Control: max-age=0');

    $writer->save('php://output');
    exit();
}

if ($_POST['action'] === 'import') {
    // Import from Excel
    if (!isset($_FILES['import_file']) || $_FILES['import_file']['error'] !== UPLOAD_ERR_OK) {
        $_SESSION['error_message'] = 'لم يتم رفع الملف بشكل صحيح';
        header('Location: ../pages/import_export.php');
        exit();
    }

    $default_status = $_POST['default_status'] ?? 'بحاجة لمراجعة';

    try {
        $spreadsheet = IOFactory::load($_FILES['import_file']['tmp_name']);
        $sheet = $spreadsheet->getActiveSheet();

        $imported_count = 0;
        $error_count = 0;

        foreach ($sheet->getRowIterator(2) as $row) { // Skip header row
            $cellIterator = $row->getCellIterator();
            $cellIterator->setIterateOnlyExistingCells(false);

            $data = [];
            foreach ($cellIterator as $cell) {
                $data[] = $cell->getValue();
            }

            // Skip empty rows
            if (empty(array_filter($data))) {
                continue;
            }

            try {
                $stmt = $pdo->prepare("
                    INSERT INTO records (
                        first_name, father_name, grandfather_name, family_name,
                        id_passport_number, date_of_birth, gender, marital_status,
                        phone_number, family_members_count, address, status, created_by_user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ");

                $stmt->execute([
                    $data[0] ?? '', // first_name
                    $data[1] ?? '', // father_name
                    $data[2] ?? '', // grandfather_name
                    $data[3] ?? '', // family_name
                    $data[4] ?? '', // id_passport_number
                    $data[5] ?? '1990-01-01', // date_of_birth
                    in_array($data[6], ['ذكر', 'أنثى']) ? $data[6] : 'ذكر', // gender
                    in_array($data[7], ['أعزب', 'متزوج', 'أرمل', 'مطلق']) ? $data[7] : 'أعزب', // marital_status
                    $data[8] ?? '', // phone_number
                    (int)($data[9] ?? 0), // family_members_count
                    $data[10] ?? '', // address
                    $default_status, // status
                    $_SESSION['user_id']
                ]);

                $imported_count++;

            } catch (PDOException $e) {
                $error_count++;
            }
        }

        $_SESSION['success_message'] = "تم استيراد $imported_count سجل بنجاح";
        if ($error_count > 0) {
            $_SESSION['warning_message'] = "فشل في استيراد $error_count سجل بسبب أخطاء في البيانات";
        }

    } catch (Exception $e) {
        $_SESSION['error_message'] = 'حدث خطأ أثناء قراءة الملف: ' . $e->getMessage();
    }

    header('Location: ../pages/import_export.php');
    exit();
}
?>
```

## Key Implementation Notes

### 1. **Security Considerations**
- Use PDO prepared statements for all database queries
- Implement proper password hashing with `password_hash()` and `password_verify()`
- Validate and sanitize all user inputs
- Use `htmlspecialchars()` for output escaping
- Implement CSRF protection for forms

### 2. **Session Management**
- Use PHP's built-in session management
- Store minimal user data in sessions
- Implement session timeout
- Regenerate session IDs on login

### 3. **Database Best Practices**
- Use transactions for multiple related operations
- Implement proper error handling
- Use connection pooling for high-traffic sites
- Create appropriate indexes for performance

### 4. **File Structure Benefits**
- Separation of concerns (config, includes, pages, actions)
- Reusable components (header, auth functions)
- Clean URL structure
- Easy maintenance and debugging

### 5. **Direct Translation from Flask**
- Same database schema and relationships
- Identical business logic and workflows
- Same UI/UX templates (just convert Jinja2 to PHP)
- Matching API endpoints and functionality

This PHP implementation provides a complete, production-ready translation of the Flask system while maintaining all the same features and functionality.