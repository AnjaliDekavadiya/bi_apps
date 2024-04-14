//$.ajax({
//    url: '/fetch_testimonials',
//    method: 'GET',
//    dataType: 'json',
//    success: function (data) {
//        $.each(data, function (index, testimonial) {
//            var blockquote = $('<blockquote>').addClass('custom_blockquote custom_blockquote_classic custom_animable blockquote');
//            var quoteIcon = $('<i>').addClass('custom_blockquote_icon fa fa-1x fa-quote-left bg-o-color-2 rounded');
//            var content = $('<div>').addClass('custom_blockquote_content bg-100');
//            var header = $('<div>').addClass('custom_testimonial_header');
//            var name = $('<p>').html('<b>' + testimonial.name + '</b>');
//            var testimonialContent = $('<div>').addClass('custom_testimonial_content');
//            var feedback = $('<p>').text(testimonial.feedback);
//
//            header.append(name);
//            testimonialContent.append(feedback);
//            content.append(header, testimonialContent);
//            blockquote.append(quoteIcon, content);
//
//            $('#testimonial-carousel').append(blockquote);
//        });
//        var script = document.createElement('script');
//        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js';
//
//        document.head.appendChild(script);
//
//        $(document).ready(function () {
//            $(".owl-carousel").owlCarousel({
//                items: 1,
//                loop: true,
//                autoplay: true,
//                autoplayTimeout: 4000,
//                margin: 20,
//                dots: true,
//                nav: false
//            });
//            $("a").on('click', function (event) {
//                if (this.hash !== "") {
//                    event.preventDefault();
//                    const hash = this.hash;
//                    $('html, body').animate({
//                        scrollTop: $(hash).offset().top
//                    }, 800, function () {
//                        window.location.hash = hash;
//                    });
//                }
//            });
//        });
//
//    },
//    error: function (xhr, status, error) {
//        console.error("Error fetching testimonials: " + error);
//    }
//});