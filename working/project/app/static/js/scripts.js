 const btn=document.getElementById('toTop')
window.addEventListener('scroll',()=> {
  btn.style.opacity = window.scrollY > 300 ? '1' : '0';
  btn.style.pointerEvents = window.scrollY > 300 ? 'auto' : 'none';
});
btn.addEventListener('click',()=>{
  window.scrollTo({top: 0,behavior: 'smooth'});
})
const call1=document.getElementById('contact')
const url1 = call1.getAttribute('data_url')

call1.addEventListener('click',()=>{
  window.open(url1)
})
const about1=document.getElementById('aboutus')
const url2 = about1.getAttribute('data_url')


about1.addEventListener('click',()=>{
  window.open(url2)
})
const services1 = document.getElementById('mservices')
const url3 = services1.getAttribute('data_url')

services1.addEventListener('click',()=>{
  window.open(url3)
})

const logo2=document.getElementById('mlogo')
const url4 = logo2.getAttribute('data_url')

logo2.addEventListener('click',()=>{
  window.open(url4)
})


const animatedImage = document.getElementById('animated-image');
const redirectTime = 3000; // 5 ثانیه انتظار
// استفاده از آدرس صفحه اصلی که از attribute تصویر گرفته شده
const homePageUrl = animatedImage.getAttribute('data_url'); 

// افزودن کلاس برای انیمیشن fade-in پس از بارگذاری کامل صفحه
window.addEventListener('load', () => {
    // مطمئن شوید کلاس fade-in در CSS تعریف شده است
    animatedImage.classList.add('fade-in'); 
});

// هدایت کاربر پس از زمان مشخص شده
setTimeout(() => {
    window.location.href = homePageUrl;
}, redirectTime);