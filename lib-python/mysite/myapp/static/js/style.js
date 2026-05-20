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

function openBorrowModal(bookId, button) {
  document.getElementById('borrowBookId').value = bookId;
  document.getElementById('expectedReturnDate').value = '';
  document.getElementById('borrowNote').value = '';
  currentBorrowButton = button;
  
  var borrowModal = new bootstrap.Modal(document.getElementById('borrowModal'));
  borrowModal.show();
}

document.addEventListener('DOMContentLoaded', function() {
  const confirmBtn = document.getElementById('confirmBorrowBtn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
      const bookId = document.getElementById('borrowBookId').value;
      const expectedDate = document.getElementById('expectedReturnDate').value;
      const note = document.getElementById('borrowNote').value;
      
      if (!expectedDate) {
        alert("Vui lòng chọn ngày dự kiến trả!");
        return;
      }
      
      fetch(`/book/${bookId}/borrow/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          expected_return_date: expectedDate,
          note: note
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          if (currentBorrowButton) {
            currentBorrowButton.outerHTML = `
              <button class="btn-view disabled" disabled>
                <i class="bi bi-book"></i> Đã Mượn
              </button>`;
          }
          var modalEl = document.getElementById('borrowModal');
          var modal = bootstrap.Modal.getInstance(modalEl);
          modal.hide();
          alert("Mượn sách thành công!");
        } else {
          alert(data.message);
        }
      })
      .catch(error => {
        console.error('Lỗi:', error);
        alert('Đã xảy ra lỗi khi mượn sách.');
      });
    });
  }
});
document.getElementById("uploadForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const formData = new FormData();
  const fileInput = document.getElementById("imageInput");
  if (!fileInput.files.length) return;

  formData.append("image", fileInput.files[0]);

  fetch("{% url 'upload_cover' %}", {
    method: "POST",
    headers: {
      "X-CSRFToken": "{{ csrf_token }}"
    },
    body: formData
  })
  .then(res => res.text())
  .then(html => {
    document.getElementById("resultArea").innerHTML = html;
  })
  .catch(err => {
    document.getElementById("resultArea").innerHTML = "Lỗi xử lý ảnh.";
    console.error(err);
  });
});