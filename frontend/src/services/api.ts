import axios from "axios";
import toast from "react-hot-toast";

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api` : "https://firmware-analysis-workflow-simulator.onrender.com",
    headers: {
        "Content-Type": "application/json",
    },
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        let message = error.response?.data?.detail || error.message || "An unexpected error occurred";
        
        if (error.code === 'ERR_NETWORK') {
            message = "Backend offline or Server unavailable (Network Error).";
        } else if (error.response?.status === 404) {
            message = "Endpoint not found.";
        } else if (error.code === 'ECONNABORTED') {
            message = "Connection timeout.";
        }
        
        if (typeof window !== "undefined") {
            toast.error(message, {
                position: "bottom-right",
                duration: 4000,
            });
        }
        return Promise.reject(error);
    }
);

export default api;
