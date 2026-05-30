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
          window.addEventListener('scroll',()=>{
            call1.style.opacity = window.scrollY > 300 ? '1' : '0';
            call1.style.pointerEvents = window.scrollY> 300 ? 'auto' : 'none';
          })
          
          call1.addEventListener('click',()=>{
            window.open(url1)
          })