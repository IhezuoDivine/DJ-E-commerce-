 document.addEventListener('DOMContentLoaded', function () {
  

  const menubtn = document.getElementById("menu");
  const closebtn = document.getElementById("close");
  const category = document.getElementById("categorycontainer");
  const viewmorecollection = document.getElementById("viewmorecollection");
  const newcollectionimghide = document.getElementById("newcollectionimghide");
  const allproductpagehide = document.getElementById("allproductpagehide");
  const allproductviewmore = document.getElementById("allproductviewmore");


  menubtn.addEventListener("click",function(event){
    event.preventDefault();
    category.style.display="block";
    menubtn.style.display = 'none';
    closebtn.style.display="inline";
  });

  closebtn.addEventListener('click', function (event) {
    event.preventDefault();
    category.style.display = 'none';
    closebtn.style.display = 'none';
    menubtn.style.display = 'inline';
  });


  viewmorecollection.addEventListener("click",function(event){
    event.preventDefault();
   
    if (getComputedStyle(newcollectionimghide).display === "none") {
      newcollectionimghide.style.display = "grid"; // or "block", depending on your layout
      viewmorecollection.textContent="View Less"
    }
   else {
      newcollectionimghide.style.display = "none";
      viewmorecollection.textContent="View More Collection"
    }
  });

  allproductviewmore.addEventListener("click", function(event){
    event.preventDefault();

    if (getComputedStyle(allproductpagehide).display === "none"){
      allproductpagehide.style.display = "grid";
      allproductviewmore.textContent = "View Less"
    }
    else {
      allproductpagehide.style.display ="none";
      allproductviewmore.textContent = "View More"
    }
  });
  
  // Map each button ID to the section ID it should show
  const viewMap = {
    homebtn: 'main',
    signupbtn: 'signup',
    profilebtn: 'profile',
    checkoutbtn: 'checkout',
    aboutusbtn: 'aboutus',
    privacybtn: 'privacy',
    contactusbtn: 'contactus',
    settingsbtn: 'settings'
  };

  // Get a list of all section IDs to hide
  const allSections = Object.values(viewMap).concat('cart');

  // Show only the selected section
  function showOnly(idToShow) {
    allSections.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.style.display = id === idToShow ? 'block' : 'none';
      }
    });
  }
  
  // Add click listeners to all linkers
  Object.entries(viewMap).forEach(([btnId, targetId]) => {
    
    const btn = document.getElementById(btnId);  
    if (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        showOnly(targetId);
      });
    }
  });

  const cartIcons = document.querySelectorAll('.fa-shopping-cart');
  cartIcons.forEach(icon => {
    icon.addEventListener("click", function (e) {
      e.preventDefault();
      showOnly('cart');
    });
  });

  //

  // Show only home on page load
  showOnly('main');


  // Class-based mapping
const classOnlyMap = {
  aboutus: 'aboutus',
  contactus: 'contactus',
  checkout: 'checkout',
  privacy: 'privacy'
};

function showOnlyClassSection(targetId) {
  const allSections = Object.values(classOnlyMap).concat('main');
  allSections.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.style.display = id === targetId ? 'block' : 'none';
    }
  });
}

// Attach event listeners to all class-based linkers
Object.entries(classOnlyMap).forEach(([className, targetId]) => {
  const classLinks = document.querySelectorAll(`.${className}`);
  classLinks.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      showOnlyClassSection(targetId);
    });
  });
});

});

