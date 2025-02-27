// @ts-ignore
import {createI18n} from 'vue-i18n'

const messages = {
    es: {
        nav: {
            home: 'Inicio',
            hotels: 'Hoteles',
            tours: 'Tours',
            offers: 'Ofertas',
            contact: 'Contacto',
            book: 'Reservar'
        },
        hero: {
            title: 'Descubre algo nuevo',
            subtitle: 'Experimenta el confort y la elegancia sin igual en nuestros destinos'
        },
        search: {
            checkIn: 'Llegada',
            checkOut: 'Salida',
            adults: 'Adultos',
            adult: 'Adulto',
            adults_plural: 'Adultos',
            children: 'Niños',
            child: 'Niño',
            children_plural: 'Niños',
            childAge: 'Edad del niño',
            addChild: 'Agregar niño',
            removeChild: 'Quitar niño',
            search: 'Buscar',
            noChildren: 'Sin niños',
            years: 'años'
        },
        benefits: {
            title: '¿Por qué elegir Harmony?',
            wifi: {
                title: 'WiFi de Alta Velocidad',
                desc: 'Mantente conectado con acceso gratuito a internet de alta velocidad'
            },
            dining: {
                title: 'Gastronomía',
                desc: 'Experimenta la excelencia culinaria en nuestros restaurantes propios y afiliados'
            },
            location: {
                title: 'Ubicaciones Premium',
                desc: 'Situados en los destinos más codiciados del Ecuador'
            },
            spa: {
                title: 'Tours',
                desc: 'Aventurate a conocer nuevos lugares y experiencias en nuestra variedad de tours privados y compartidos'
            },
            promotions: {
                title: 'Promociones',
                desc: 'Descubre nuestras promociones y descuentos con nuestras locales aliados'
            }
        },
        features: {
            title: 'Nuestros Hoteles',
            subtitle: 'Descubre nuestras propiedades más exclusivas en destinos de ensueño',
            view: 'Ver Detalles',
            viewAll: 'Ver Todos los Hoteles',
        },
        destinations: {
            title: 'Destinos Cercanos',
            subtitle: 'Explora lugares increíbles cerca de nuestros hoteles',
            viewAll: 'Explorar Tours Disponibles',
        },
        footer: {
            about: 'Harmony Hotel Group ofrece experiencias únicas de hospitalidad de lujo en los destinos más exclusivos del mundo.',
            quickLinks: 'Enlaces Rápidos',
            links: {
                home: 'Inicio',
                hotels: 'Hoteles',
                tours: 'Tours',
                offers: 'Ofertas',
                contact: 'Contacto'
            },
            faq: {
                title: 'Preguntas Frecuentes',
                booking: '¿Cómo realizar una reserva?',
                cancellation: 'Política de cancelación',
                payment: 'Métodos de pago',
                checkin: 'Horarios de check-in/out',
                services: 'Servicios incluidos'
            },
            contact: {
                title: 'Contacto',
                address: 'Av. Gran Colombia y Huayna Capac, Cuenca, Ecuador'
            },
            rights: 'Todos los derechos reservados.',
            legal: {
                privacy: 'Política de Privacidad',
                terms: 'Términos y Condiciones',
                cookies: 'Política de Cookies'
            }
        }
    },
    en: {
        nav: {
            home: 'Home',
            hotels: 'Hotels',
            tours: 'Tours',
            offers: 'Offers',
            contact: 'Contact',
            book: 'Book Now'
        },
        hero: {
            title: 'Discover Luxury Living',
            subtitle: 'Experience unparalleled comfort and elegance at our world-class destinations'
        },
        search: {
            checkIn: 'Check In',
            checkOut: 'Check Out',
            adults: 'Adults',
            adult: 'Adult',
            adults_plural: 'Adults',
            children: 'Children',
            child: 'Child',
            children_plural: 'Children',
            childAge: 'Child age',
            addChild: 'Add child',
            removeChild: 'Remove child',
            search: 'Search',
            noChildren: 'No children',
            years: 'years'
        },
        benefits: {
            title: 'Why Choose Harmony?',
            wifi: {
                title: 'High-Speed WiFi',
                desc: 'Stay connected with complimentary high-speed internet access'
            },
            dining: {
                title: 'Fine Dining',
                desc: 'Experience culinary excellence at our gourmet restaurants'
            },
            location: {
                title: 'Prime Locations',
                desc: 'Situated in the most sought-after destinations worldwide'
            },
            spa: {
                title: 'Luxury Spa',
                desc: 'Rejuvenate your body and mind in our world-class spas'
            }
        },
        footer: {
            about: 'Harmony Hotel Group offers unique luxury hospitality experiences in the world\'s most exclusive destinations.',
            quickLinks: 'Quick Links',
            links: {
                home: 'Home',
                hotels: 'Hotels',
                tours: 'Tours',
                offers: 'Offers',
                contact: 'Contact'
            },
            faq: {
                title: 'Frequently Asked Questions',
                booking: 'How to make a reservation?',
                cancellation: 'Cancellation policy',
                payment: 'Payment methods',
                checkin: 'Check-in/out times',
                services: 'Included services'
            },
            contact: {
                title: 'Contact',
                address: '123 Main St, New York'
            },
            rights: 'All rights reserved.',
            legal: {
                privacy: 'Privacy Policy',
                terms: 'Terms & Conditions',
                cookies: 'Cookie Policy'
            }
        }
    }
}

export default createI18n({
    legacy: false,
    locale: 'es',
    fallbackLocale: 'en',
    messages
})