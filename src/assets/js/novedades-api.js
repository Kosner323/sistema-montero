// ============================================
// NOVEDADES-API.JS
// Funciones para comunicación con el backend
// ============================================

const NovedadesAPI = {
    /**
     * Obtiene todas las novedades desde el servidor
     * @returns {Promise<Array>} Lista de novedades
     */
    async getAll() {
        try {
            const response = await fetch(NOVEDADES_CONFIG.API.GET_ALL, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error en getAll():', error);
            throw error;
        }
    },

    /**
     * Crea una nueva novedad
     * @param {Object} novedadData - Datos de la novedad
     * @returns {Promise<Object>} Novedad creada
     */
    async create(novedadData) {
        try {
            const response = await fetch(NOVEDADES_CONFIG.API.CREATE, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(novedadData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al crear novedad');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error en create():', error);
            throw error;
        }
    },

    /**
     * Actualiza una novedad existente
     * @param {number} id - ID de la novedad
     * @param {Object} updateData - Datos a actualizar
     * @returns {Promise<Object>} Novedad actualizada
     */
    async update(id, updateData) {
        try {
            const response = await fetch(NOVEDADES_CONFIG.API.UPDATE(id), {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al actualizar novedad');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error en update():', error);
            throw error;
        }
    },

    /**
     * Elimina una novedad
     * @param {number} id - ID de la novedad
     * @returns {Promise<void>}
     */
    async delete(id) {
        try {
            const response = await fetch(NOVEDADES_CONFIG.API.DELETE(id), {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al eliminar novedad');
            }
        } catch (error) {
            console.error('Error en delete():', error);
            throw error;
        }
    },

    /**
     * Obtiene la lista de empresas
     * @returns {Promise<Array>} Lista de empresas
     */
    async getEmpresas() {
        try {
            const response = await fetch(NOVEDADES_CONFIG.API.GET_EMPRESAS, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Error al obtener empresas');
            }

            return await response.json();
        } catch (error) {
            console.error('Error en getEmpresas():', error);
            return [];
        }
    },

    /**
     * Obtiene la lista de usuarios
     * @param {string} empresaNit - NIT de la empresa (opcional)
     * @returns {Promise<Array>} Lista de usuarios
     */
    async getUsuarios(empresaNit = null) {
        try {
            let url = NOVEDADES_CONFIG.API.GET_USUARIOS;
            if (empresaNit) {
                url += `?empresa_nit=${empresaNit}`;
            }

            const response = await fetch(url, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Error al obtener usuarios');
            }

            return await response.json();
        } catch (error) {
            console.error('Error en getUsuarios():', error);
            return [];
        }
    },

    /**
     * Busca un usuario por su número de identificación
     * @param {string} numeroId - Número de identificación
     * @returns {Promise<Object|null>} Usuario encontrado o null
     */
    async findUsuarioById(numeroId) {
        try {
            // Primero buscar en caché
            const cached = window.usuariosCache.find(u => u.numeroId === numeroId);
            if (cached) {
                return cached;
            }

            // Si no está en caché, buscar en el servidor
            const usuarios = await this.getUsuarios();
            window.usuariosCache = usuarios;
            
            return usuarios.find(u => u.numeroId === numeroId) || null;
        } catch (error) {
            console.error('Error en findUsuarioById():', error);
            return null;
        }
    },

    /**
     * Agrega un comentario a una novedad
     * @param {number} id - ID de la novedad
     * @param {string} comment - Comentario a agregar
     * @returns {Promise<Object>} Novedad actualizada
     */
    async addComment(id, comment) {
        return this.update(id, {
            newComment: comment
        });
    },

    /**
     * Cierra un caso (marca como resuelto)
     * @param {number} id - ID de la novedad
     * @returns {Promise<Object>} Novedad actualizada
     */
    async closeCase(id) {
        return this.update(id, {
            status: 'Resuelto',
            priority: 'baja',
            priorityText: 'Resuelto'
        });
    }
};

// Exportar para uso global
window.NovedadesAPI = NovedadesAPI;