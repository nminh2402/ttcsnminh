document.addEventListener('DOMContentLoaded', function() {
    // Initialize book slider functionality if it exists
    const sliders = document.querySelectorAll('.book-slider');
    
    sliders.forEach(slider => {
      const container = slider.closest('.book-slider-container');
      if (!container) return;
      
      const prevBtn = container.querySelector('.prev-btn');
      const nextBtn = container.querySelector('.next-btn');
      const dotsContainer = container.parentElement.querySelector('.slider-dots');
      
      // Skip if elements not found
      if (!prevBtn || !nextBtn || !dotsContainer) return;
      
      // Calculate dimensions
      const bookWidth = slider.querySelector('.book-item').offsetWidth + 20; // width + gap
      const visibleWidth = slider.offsetWidth;
      const itemsPerPage = Math.floor(visibleWidth / bookWidth);
      const totalItems = slider.querySelectorAll('.book-item').length;
      const totalPages = Math.ceil(totalItems / itemsPerPage);
      
      // Create dots
      for (let i = 0; i < totalPages; i++) {
        const dot = document.createElement('span');
        dot.classList.add('dot');
        if (i === 0) dot.classList.add('active');
        dot.dataset.index = i;
        dotsContainer.appendChild(dot);
        
        dot.addEventListener('click', () => {
          currentPage = i;
          updateSlider();
        });
      }
      
      let currentPage = 0;
      
      // Update slider to current page
      function updateSlider() {
        const scrollPosition = currentPage * visibleWidth;
        slider.scrollLeft = scrollPosition;
        
        // Update dots
        dotsContainer.querySelectorAll('.dot').forEach((dot, index) => {
          if (index === currentPage) {
            dot.classList.add('active');
          } else {
            dot.classList.remove('active');
          }
        });
        
        // Update button states
        prevBtn.disabled = currentPage === 0;
        prevBtn.style.opacity = currentPage === 0 ? '0.5' : '1';
        
        nextBtn.disabled = currentPage === totalPages - 1;
        nextBtn.style.opacity = currentPage === totalPages - 1 ? '0.5' : '1';
      }
      
      // Initial setup
      updateSlider();
      
      // Button event listeners
      prevBtn.addEventListener('click', () => {
        if (currentPage > 0) {
          currentPage--;
          updateSlider();
        }
      });
      
      nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages - 1) {
          currentPage++;
          updateSlider();
        }
      });
      
      // Handle window resize
      window.addEventListener('resize', () => {
        // Recalculate dimensions
        const newBookWidth = slider.querySelector('.book-item').offsetWidth + 20;
        const newVisibleWidth = slider.offsetWidth;
        const newItemsPerPage = Math.floor(newVisibleWidth / newBookWidth);
        const newTotalPages = Math.ceil(totalItems / newItemsPerPage);
        
        // Reset dots
        dotsContainer.innerHTML = '';
        for (let i = 0; i < newTotalPages; i++) {
          const dot = document.createElement('span');
          dot.classList.add('dot');
          if (i === currentPage) dot.classList.add('active');
          dot.dataset.index = i;
          dotsContainer.appendChild(dot);
          
          dot.addEventListener('click', () => {
            currentPage = i;
            updateSlider();
          });
        }
        
        // Ensure current page is valid
        if (currentPage >= newTotalPages) {
          currentPage = newTotalPages - 1;
        }
        
        // Update slider
        updateSlider();
      });
    });
  });
  document.addEventListener('DOMContentLoaded', function() {
  const backToTopButton = document.getElementById('back-to-top');
  
  // Show/hide button based on scroll position
  window.addEventListener('scroll', function() {
      if (window.scrollY > 300) {
          backToTopButton.classList.add('visible');
      } else {
          backToTopButton.classList.remove('visible');
      }
  });
  
  // Custom smooth scroll with slower speed
  backToTopButton.addEventListener('click', function() {
      const scrollToTop = () => {
          // Current scroll position
          const currentPosition = window.scrollY || document.documentElement.scrollTop;
          
          if (currentPosition > 0) {
              // Slow down by increasing the divisor (10 is slower than default)
              window.requestAnimationFrame(scrollToTop);
              window.scrollTo(0, currentPosition - currentPosition / 10);
          }
      };
      scrollToTop();
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

let currentBorrowButton = null;

function openBorrowModal(bookId, button, bookTitle) {
  document.getElementById('borrowBookId').value = bookId;
  const inputTitle = document.getElementById('borrowBookTitle');
  if (inputTitle) inputTitle.value = bookTitle || '';
  
  document.getElementById('expectedReturnDate').value = '';
  document.getElementById('borrowNote').value = '';
  
  const feePreview = document.getElementById('feePreview');
  if (feePreview) feePreview.textContent = '';
  
  const step1 = document.getElementById('step1');
  const step2 = document.getElementById('step2');
  if (step1) step1.style.display = '';
  if (step2) step2.style.display = 'none';

  currentBorrowButton = button;
  
  var borrowModal = new bootstrap.Modal(document.getElementById('borrowModal'));
  borrowModal.show();
}

document.addEventListener('DOMContentLoaded', function() {
  const dateInput = document.getElementById('expectedReturnDate');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    dateInput.addEventListener('change', function() {
      const d = new Date(this.value);
      const now = new Date();
      now.setHours(0,0,0,0);
      const days = Math.round((d - now) / 86400000);
      const fee = days > 0 ? days * 3000 : 0;
      const preview = document.getElementById('feePreview');
      if (preview) {
        preview.textContent = days > 0
          ? `Ước tính: ${days} ngày × 3.000 VND = ${fee.toLocaleString('vi-VN')} VND`
          : '';
      }
    });
  }

  const confirmBtn = document.getElementById('confirmBorrowBtn');
  const submitBtn = document.getElementById('btnSubmitBorrow');
  let currentExpectedDate = '';
  let currentNote = '';

  if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
      const expectedDate = document.getElementById('expectedReturnDate').value;
      const note = document.getElementById('borrowNote').value;
      
      if (!expectedDate) {
        alert("Vui lòng chọn ngày dự kiến trả!");
        return;
      }

      const d = new Date(expectedDate);
      const now = new Date();
      now.setHours(0,0,0,0);
      const days = Math.round((d - now) / 86400000);
      
      if (days <= 0) {
        alert('Ngày dự kiến trả phải lớn hơn ngày hiện tại!');
        return;
      }

      currentExpectedDate = expectedDate;
      currentNote = note;
      const fee = days * 3000;

      const bank_id = "MB";
      const account_no = "0774504240205";
      const account_name = "LE NGUYEN NHAT MINH";
      let title = '';
      const inputTitle = document.getElementById('borrowBookTitle');
      if (inputTitle) title = inputTitle.value;
      if (!title) title = 'Sach';
      
      const addInfo = "Muon sach " + title.substring(0, 20);
      const qr_url = `https://img.vietqr.io/image/${bank_id}-${account_no}-compact2.jpg?amount=${fee}&addInfo=${encodeURIComponent(addInfo)}&accountName=${encodeURIComponent(account_name)}`;

      const step1 = document.getElementById('step1');
      const step2 = document.getElementById('step2');
      if (step1) step1.style.display = 'none';
      if (step2) step2.style.display = '';

      const qrImg = document.getElementById('qrImage');
      if (qrImg) qrImg.src = qr_url;
      const tFee = document.getElementById('qrTotalFee');
      if (tFee) tFee.textContent = fee.toLocaleString('vi-VN') + ' VND';
      const detail = document.getElementById('qrFeeDetail');
      if (detail) detail.textContent = `${days} ngày × 3.000 VND/ngày`;
      
      const elAcc = document.getElementById('qrAccount');
      if (elAcc) elAcc.textContent = account_no;
      const elName = document.getElementById('qrName');
      if (elName) elName.textContent = account_name;
      const elCont = document.getElementById('qrContent');
      if (elCont) elCont.textContent = addInfo;
    });
  }

  if (submitBtn) {
    submitBtn.addEventListener('click', function() {
      const bookId = document.getElementById('borrowBookId').value;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Đang gửi...';

      fetch(`/book/${bookId}/borrow/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          expected_return_date: currentExpectedDate,
          note: currentNote
        })
      })
      .then(r => r.json())
      .then(data => {
        submitBtn.disabled = false;
        submitBtn.textContent = '✅ Đã chuyển khoản, gửi yêu cầu';

        if (data.success) {
          bootstrap.Modal.getInstance(document.getElementById('borrowModal')).hide();
          if (currentBorrowButton) {
            currentBorrowButton.outerHTML = `<button class="btn-view disabled" disabled><i class="bi bi-clock"></i> Chờ duyệt</button>`;
          }
          alert('Đã gửi yêu cầu mượn sách. Vui lòng chờ admin duyệt!');
        } else {
          alert(data.message);
        }
      })
      .catch(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = '✅ Đã chuyển khoản, gửi yêu cầu';
        alert('Đã xảy ra lỗi, vui lòng thử lại.');
      });
    });
  }
});
const uploadForm = document.getElementById("uploadForm");
if (uploadForm) {
  uploadForm.addEventListener("submit", function(e) {
    e.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById("imageInput");
    if (!fileInput || !fileInput.files.length) return;

    formData.append("image", fileInput.files[0]);

    fetch("/search-image/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie('csrftoken')
      },
      body: formData
    })
    .then(res => res.text())
    .then(html => {
      const resultArea = document.getElementById("resultArea");
      if (resultArea) resultArea.innerHTML = html;
    })
    .catch(err => {
      const resultArea = document.getElementById("resultArea");
      if (resultArea) resultArea.innerHTML = "Lỗi xử lý ảnh.";
      console.error(err);
    });
  });
}