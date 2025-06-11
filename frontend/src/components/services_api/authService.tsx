export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  jwt?: string;
  error?: string;
}

export interface User {
  email: string;
  username: string;
  id: number;
}

class AuthService {
  private baseURL = "http://localhost:9000/auth";

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await fetch(`${this.baseURL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
      });

      return await response.json();
    } catch (error) {
      throw new Error("Network error");
    }
  }

  // Decodificar JWT para obtener información del usuario
  decodeToken(token: string): User | null {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        id: parseInt(payload.sub),
        email: payload.email || '',
        username: payload.username || ''
      };
    } catch (error) {
      return null;
    }
  }

  setToken(token: string, remember: boolean = false) {
    if (remember) {
      localStorage.setItem("authToken", token);
    } else {
      sessionStorage.setItem("authToken", token);
    }
  }

  setUser(user: User) {
    const storage = localStorage.getItem("authToken") ? localStorage : sessionStorage;
    storage.setItem("userInfo", JSON.stringify(user));
  }

  getToken(): string | null {
    return localStorage.getItem("authToken") || sessionStorage.getItem("authToken");
  }

  getUser(): User | null {
    const userInfo = localStorage.getItem("userInfo") || sessionStorage.getItem("userInfo");
    return userInfo ? JSON.parse(userInfo) : null;
  }

  removeToken() {
    localStorage.removeItem("authToken");
    sessionStorage.removeItem("authToken");
    localStorage.removeItem("userInfo");
    sessionStorage.removeItem("userInfo");
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  logout() {
    this.removeToken();
  }

  // Método para hacer peticiones autenticadas
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getToken();
    
    if (!token) {
      throw new Error("No authentication token found");
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    };

    return fetch(url, {
      ...options,
      headers,
    });
  }
}

export default new AuthService();
