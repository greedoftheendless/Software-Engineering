document.querySelectorAll(".tab-btn").forEach((button) => {
  button.addEventListener("click", () => {
    // Remove active class from all buttons and forms
    document
      .querySelectorAll(".tab-btn")
      .forEach((btn) => btn.classList.remove("active"));
    document.querySelectorAll(".form").forEach((form) => {
      form.classList.remove("active");
      form.style.opacity = 0; // Reset opacity for the transition
    });

    // Add active class to clicked button and corresponding form
    button.classList.add("active");
    const formId = button.dataset.form;
    const activeForm = document.getElementById(formId);
    activeForm.classList.add("active");

    // Add a small delay before applying opacity to trigger transition smoothly
    setTimeout(() => {
      activeForm.style.opacity = 1; // Smooth fade in
    }, 10);

    // Change title based on the selected form
    const pageTitle = document.getElementById("page-title");
    if (formId === "login-form") {
      pageTitle.textContent = "Online Mess Management System";
    } else {
      pageTitle.textContent = "Welcome to Mess Mate";
    }
  });
});
