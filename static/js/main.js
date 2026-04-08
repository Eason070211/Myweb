// Main JavaScript file for the website
document.addEventListener('DOMContentLoaded', function() {
    // Add any interactive functionality here
    console.log('Website loaded successfully!');
    
    // Example: Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});