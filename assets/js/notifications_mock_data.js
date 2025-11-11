/**
 * Mock Data para Notificaciones
 * Este archivo simula las respuestas del API hasta que conectes con tu backend real
 * 
 * INSTRUCCIONES:
 * 1. Incluir este script ANTES del _header.html en tus páginas HTML:
 *    <script src="../assets/js/notifications-mock.js"></script>
 * 
 * 2. Una vez que tu API real esté lista, simplemente elimina este script
 *    y las funciones del header usarán automáticamente tu API
 */

(function() {
  // Solo activar mock si estamos en desarrollo (puedes cambiar esta condición)
  const USE_MOCK = true; // Cambiar a false cuando tengas el API real
  
  if (!USE_MOCK) return;
  
  console.log('📢 Usando datos mock para notificaciones');
  
  // Datos de ejemplo
  const mockNotifications = [
    {
      id: 1,
      title: 'Nueva Novedad Registrada',
      message: 'Se ha registrado una nueva novedad para Empresa ABC',
      type: 'primary',
      icon: 'bell',
      link: 'novedades.html?id=1',
      read: false,
      timeAgo: 'Hace 5 minutos',
      timestamp: new Date(Date.now() - 5 * 60 * 1000)
    },
    {
      id: 2,
      title: 'Pago Pendiente',
      message: 'El pago de planilla de Empresa XYZ está pendiente',
      type: 'warning',
      icon: 'alert-circle',
      link: 'pagos.html?id=2',
      read: false,
      timeAgo: 'Hace 1 hora',
      timestamp: new Date(Date.now() - 60 * 60 * 1000)
    },
    {
      id: 3,
      title: 'Documento Aprobado',
      message: 'El formulario 2024-001 ha sido aprobado',
      type: 'success',
      icon: 'check-circle',
      link: 'formularios.html?id=3',
      read: true,
      timeAgo: 'Hace 3 horas',
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000)
    }
  ];
  
  // Interceptar fetch para simular API
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    const url = args[0];
    
    // GET /api/notifications
    if (url === '/api/notifications') {
      console.log('🔄 Mock: GET /api/notifications');
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockNotifications)
      });
    }
    
    // POST /api/notifications/mark-all-read
    if (url === '/api/notifications/mark-all-read') {
      console.log('🔄 Mock: POST /api/notifications/mark-all-read');
      mockNotifications.forEach(n => n.read = true);
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ success: true })
      });
    }
    
    // POST /api/notifications/:id/read
    if (url.match(/\/api\/notifications\/\d+\/read/)) {
      const id = parseInt(url.match(/\/api\/notifications\/(\d+)\/read/)[1]);
      console.log(`🔄 Mock: POST /api/notifications/${id}/read`);
      const notification = mockNotifications.find(n => n.