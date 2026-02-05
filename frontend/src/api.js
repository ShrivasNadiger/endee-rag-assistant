/**
 * API Client for RAG Backend
 */

import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Ingest documents into the system
 * @param {File[]} files - Array of File objects
 * @returns {Promise} - Ingestion result
 */
export const ingestDocuments = async (files) => {
    const formData = new FormData();
    files.forEach((file) => {
        formData.append('files', file);
    });

    const response = await axios.post(`${API_BASE_URL}/ingest`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};

/**
 * Query the RAG system
 * @param {string} query - User query
 * @param {number} topK - Number of chunks to retrieve
 * @returns {Promise} - Query result with answer and metadata
 */
export const queryRAG = async (query, topK = 5) => {
    const response = await api.post('/query', {
        query,
        top_k: topK,
    });

    return response.data;
};

/**
 * Get system statistics
 * @returns {Promise} - System stats
 */
export const getStats = async () => {
    const response = await api.get('/stats');
    return response.data;
};

export default api;
