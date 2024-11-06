document.addEventListener('DOMContentLoaded', function () {
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add mobile menu functionality
    const menuButton = document.createElement('button');
    menuButton.classList.add('menu-toggle');
    menuButton.innerHTML = `
    <svg viewBox="0 0 24 24" width="24" height="24">
    <path fill="currentColor" d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"/>
    </svg>
    `;

    const navLinks = document.querySelector('.nav-links');
    menuButton.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    document.querySelector('.navbar-content').appendChild(menuButton);
});