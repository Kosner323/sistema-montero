// ============================================================================
// LAYOUT LOADER - Portal Montero
// Carga componentes del layout (header, sidebar, footer) y maneja la inicialización
// ============================================================================

/**
 * Carga un fragmento de HTML en un elemento del DOM.
 * @param {string} elementId - ID del elemento donde cargar el HTML
 * @param {string} filePath - Ruta del archivo HTML a cargar
 * @returns {Promise<boolean>} - True si se cargó correctamente
 */
async function loadHtmlTemplate(elementId, filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error(`Fetch failed: ${response.status}`);
        }

        const html = await response.text();
        const element = document.getElementById(elementId);

        if (element) {
            element.innerHTML = html;
            console.log(`✅ ${elementId} loaded from ${filePath}`);
            return true;
        } else {
            console.warn(`⚠️ Placeholder ${elementId} not found in DOM`);
            return false;
        }
    } catch (error) {
        console.error(`❌ Error loading ${filePath}:`, error);
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<p class="text-danger p-3">Error loading ${elementId}</p>`;
        }
        return false;
    }
}

/**
 * Marca el enlace activo en el sidebar según la página actual
 */
function highlightActiveSidebarLink() {
    try {
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const sidebar = document.getElementById('sidebar-placeholder'); // Cambiado a placeholder ID

        // Verificar que el sidebar esté cargado
        if (!sidebar || !sidebar.querySelector('.pc-navbar')) {
            console.warn('⚠️ Sidebar content not ready, retrying highlight...');
            setTimeout(highlightActiveSidebarLink, 100); // Reintentar después de 100ms
            return;
        }

        // Resetear todos los items activos
        sidebar.querySelectorAll('li.pc-item.active, li.pc-item.pc-trigger').forEach(li => {
            li.classList.remove('active', 'pc-trigger');
            const link = li.querySelector('a.pc-link.is-active');
            if (link) {
                link.classList.remove('is-active');
            }
            // Ocultar submenús abiertos si es necesario
            const submenu = li.querySelector('.pc-submenu');
            if (submenu && !li.classList.contains('pc-trigger')) { // Solo si no es el padre activo
                 submenu.style.display = 'none';
            }
        });

        // Activar el enlace actual y sus padres
        const activeLink = sidebar.querySelector(`a.pc-link[href$="${currentPage}"]`);
        if (activeLink) {
            const activeLi = activeLink.closest('li.pc-item');
            if (activeLi) {
                activeLi.classList.add('active');
                activeLink.classList.add('is-active');

                // Abrir y activar submenús padres si existen
                let parent = activeLi.closest('ul.pc-submenu');
                while (parent) {
                    const parentLi = parent.closest('li.pc-item.pc-hasmenu');
                    if (parentLi) {
                        parentLi.classList.add('active', 'pc-trigger');
                        parent.style.display = 'block'; // Asegurar que el submenú esté visible
                        parent = parentLi.closest('ul.pc-submenu'); // Seguir subiendo
                    } else {
                        break; // Salir si no hay más padres
                    }
                }
            }
        }

        console.log(`✅ Active link highlighted for: ${currentPage}`);
    } catch(e) {
        console.error('❌ Error highlighting active link:', e);
    }
}


/**
 * Configura el nombre de usuario en el header
 */
function setupUserName() {
    const trySetup = () => {
        const storedUserName = sessionStorage.getItem('userName');
        // Usar un selector más específico si hay múltiples elementos con la misma clase
        const userNameDisplay = document.querySelector('#header-placeholder .header-user-profile .text-white'); // Ajusta si la estructura cambia

        if (userNameDisplay) {
            // Asumiendo que el nombre es el elemento h6
             const nameElement = userNameDisplay.closest('.grow')?.querySelector('h6');
             if(nameElement) {
                 nameElement.textContent = storedUserName || 'Usuario';
                 console.log('✅ User name configured');
             } else {
                  console.warn('⚠️ Name element (h6) not found inside user profile dropdown');
             }
            return true;
        }
        return false;
    };

    // Reintentar si el elemento no está listo
    if (!trySetup()) {
        console.warn('⚠️ User name display element not ready, retrying...');
        setTimeout(trySetup, 300); // Aumentar delay si es necesario
    }
}


/**
 * Configura los botones de logout
 */
function setupLogoutButtons() {
    // Esperar un poco más para asegurar que handleLogout (definido en HTML) esté disponible
    setTimeout(() => {
        const setupButton = (buttonSelector) => { // Usar selector en lugar de ID
            const button = document.querySelector(buttonSelector);
            if (button) {
                // Limpiar listeners anteriores clonando el botón (buena práctica)
                const newButton = button.cloneNode(true);
                button.parentNode.replaceChild(newButton, button);

                // Adjuntar nuevo listener
                if (typeof handleLogout === 'function') { // handleLogout debe ser global
                    newButton.addEventListener('click', (e) => {
                        e.preventDefault();
                        handleLogout(); // Llama a la función global
                    });
                    console.log(`✅ Logout listener attached to ${buttonSelector}`);
                } else {
                    // Si handleLogout no es global, intentar buscarla en el scope del header
                    // O definir handleLogout directamente aquí o en un script global cargado antes
                    console.warn(`⚠️ handleLogout not defined globally for ${buttonSelector}. Logout might fail.`);
                     // Fallback simple si no se encuentra handleLogout
                     newButton.addEventListener('click', (e) => {
                         e.preventDefault();
                         console.log("Attempting basic logout...");
                         fetch('/api/logout', { method: 'POST', credentials: 'include' })
                           .finally(() => window.location.href = '/login');
                     });

                }
            } else {
                 console.warn(`⚠️ Logout button not found: ${buttonSelector}`);
            }
        };

        // Selectores para los botones de logout (ajusta si cambian)
        setupButton('#header-placeholder .dropdown-item i.ti-power'); // Botón en dropdown de settings
        setupButton('#header-placeholder .dropdown-user-profile button'); // Botón principal en dropdown de perfil
    }, 500); // Aumentar delay si handleLogout se define tarde
}

/**
 * Inicializa el sidebar móvil
 */
function initializeMobileSidebar() {
    // Esperar a que el sidebar HTML esté cargado
    setTimeout(() => {
        const mobileCollapse = document.getElementById('mobile-collapse');
        const sidebarHide = document.getElementById('sidebar-hide');
        const sidebar = document.querySelector('.pc-sidebar'); // Selector directo

        if (!sidebar) {
             console.warn("⚠️ Sidebar element (.pc-sidebar) not found for mobile init.");
             return;
        }

        if (mobileCollapse) {
            mobileCollapse.addEventListener('click', (e) => {
                e.preventDefault();
                sidebar.classList.toggle('mob-sidebar-active');
                // Añadir/quitar overlay
                 let overlay = sidebar.querySelector('.pc-menu-overlay');
                 if (sidebar.classList.contains('mob-sidebar-active')) {
                     if (!overlay) {
                         overlay = document.createElement('div');
                         overlay.className = 'pc-menu-overlay';
                         sidebar.appendChild(overlay);
                         overlay.addEventListener('click', () => {
                              sidebar.classList.remove('mob-sidebar-active');
                              overlay.remove();
                         });
                     }
                 } else if (overlay) {
                     overlay.remove();
                 }
            });
        }

        if (sidebarHide) {
            sidebarHide.addEventListener('click', (e) => {
                e.preventDefault();
                // Alternar clase en body o html para colapsar/expandir en desktop
                document.querySelector('html').classList.toggle('pc-sidebar-hide');
            });
        }

        // Cerrar sidebar al hacer click fuera en móvil (si overlay no funciona)
        // document.addEventListener('click', (e) => {
        //     if (sidebar && sidebar.classList.contains('mob-sidebar-active')) {
        //         if (!sidebar.contains(e.target) &&
        //             !mobileCollapse?.contains(e.target) &&
        //             window.innerWidth < 1024) { // Asegurar que sea pantalla móvil
        //             sidebar.classList.remove('mob-sidebar-active');
        //             const overlay = sidebar.querySelector('.pc-menu-overlay');
        //             if(overlay) overlay.remove();
        //         }
        //     }
        // });

        console.log('✅ Mobile sidebar initialized (listeners attached).');
    }, 150); // Pequeño delay para asegurar que el HTML del sidebar exista
}


/**
 * Oculta el loader
 */
function hideLoader() {
    const loader = document.querySelector('.loader-bg');
    if (loader) {
        loader.style.display = 'none';
        console.log('✅ Loader hidden');
    }
}

// ============================================================================
// EJECUCIÓN PRINCIPAL
// ============================================================================

(async function main() {
    console.log('🚀 layout-loader.js starting...');

    try {
        // 1. Cargar templates HTML
        console.log('📥 Loading HTML templates...');
        const [sidebarLoaded, headerLoaded, footerLoaded] = await Promise.all([
            loadHtmlTemplate('sidebar-placeholder', '_sidebar.html'),
            loadHtmlTemplate('header-placeholder', '_header.html'),
            loadHtmlTemplate('footer-placeholder', '_footer.html')
        ]);
        console.log('✅ HTML Templates loaded');

        // 2. Esperar un momento para que el navegador procese el HTML
        await new Promise(resolve => setTimeout(resolve, 50)); // Pequeño delay

        // --- ❗️ INICIO DE CAMBIOS: Comentar inicializaciones ❗️ ---

        // 3. Inicializar funcionalidad del header (AHORA LO HARÁ [pagina]-main.js o script específico)
        // if (headerLoaded && typeof initializeHeaderFunctionality === 'function') {
        //     console.log("layout-loader: Omitiendo initializeHeaderFunctionality() - main.js/page script se encargará.");
        //     // initializeHeaderFunctionality(); // COMENTADO
        // } else if (headerLoaded) {
        //      console.warn("layout-loader: Header HTML cargado, pero initializeHeaderFunctionality() no está definida.");
        // }


        // 4. Configurar sidebar (Highlight y móvil SÍ pueden quedarse aquí si funcionan bien)
        if (sidebarLoaded) {
            highlightActiveSidebarLink(); // Marcar enlace activo
            initializeMobileSidebar(); // Configurar botones de toggle
        }

        // 5. Configurar usuario y logout (Estos SÍ pueden quedarse aquí, dependen solo del HTML cargado)
        if (headerLoaded) {
            setupUserName(); // Poner nombre de usuario
            // setupLogoutButtons(); // Se llama DENTRO de setupUserName o después para asegurar contexto
            // Llamar a setupLogoutButtons después de un delay mayor para asegurar que handleLogout exista
            setTimeout(setupLogoutButtons, 600);
        }

        // 6. Ocultar loader
        hideLoader();

        // 7. Inicializar iconos de Feather (AHORA LO HARÁ [pagina]-main.js o script específico)
        // const initFeather = () => { ... }; // LÓGICA COMENTADA
        // initFeather(); // LLAMADA COMENTADA
        console.log("layout-loader: Omitiendo initFeather() - main.js/page script se encargará.");


        // --- ❗️ FIN DE CAMBIOS ❗️ ---

        console.log('🎉 layout-loader.js finished successfully');

    } catch (error) {
        console.error('❌ Error in layout-loader.js:', error);
        hideLoader(); // Ocultar loader incluso si hay error
    }

    // Verificación de funciones críticas (sin cambios)
    setTimeout(() => {
        console.log('🔍 Checking critical functions after layout load:');
        console.log(`  - layout_change: ${typeof layout_change === 'function' ? '✅' : '❌'}`);
        console.log(`  - layout_change_default: ${typeof layout_change_default === 'function' ? '✅' : '❌'}`);
        // console.log(`  - handleLogout: ${typeof handleLogout === 'function' ? '✅' : '❌'}`); // Puede definirse más tarde
        console.log(`  - feather: ${typeof feather !== 'undefined' ? '✅' : '❌'}`);
        console.log(`  - bootstrap: ${typeof bootstrap !== 'undefined' ? '✅' : '❌'}`);
        console.log(`  - $: ${typeof $ !== 'undefined' ? '✅' : '❌'}`); // Verificar jQuery
    }, 1000); // Aumentar delay para dar tiempo a cargar todo
})();

// ============================================================================
// UTILIDADES ADICIONALES (Sin cambios)
// ============================================================================

/**
 * Recarga todos los componentes del layout
 */
async function reloadLayout() {
    console.log('🔄 Reloading layout...');
    await main(); // Volver a ejecutar la función principal
}

// Exponer funciones globalmente si es necesario
window.reloadLayout = reloadLayout;
// window.loadHtmlTemplate = loadHtmlTemplate; // Exponer solo si se usa desde fuera