import axios from 'axios';

const API = axios.create({ baseURL: '/api' });

export const getWeather      = (district) => API.get(`/data/weather?district=${district}`);
export const getMarket       = (district) => API.get(`/data/market?district=${district}`);
export const getAdvisory     = (district) => API.get(`/data/advisory?district=${district}`);
export const getSchemes      = ()          => API.get('/data/schemes');
export const getDistricts    = ()          => API.get('/data/districts');
export const getCrops        = ()          => API.get('/data/crops');
export const getDashboard    = (district) => API.get(`/data/dashboard?district=${district}`);
export const previewReport   = (data)     => API.post('/report/preview', data);
export const generateReport  = (data)     => API.post('/report/generate', data, { responseType: 'blob' });
export const sendChat        = (message, history) => API.post('/chat/message', { message, history });
export const getQuickTips    = ()          => API.get('/chat/quick-tips');
export const trainModels     = ()          => API.post('/report/train');

export default API;
