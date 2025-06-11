import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

const EmailVerification: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const hasVerified = useRef(false); // Flag para evitar múltiples verificaciones

  useEffect(() => {
    // Si ya se verificó, no hacer nada
    if (hasVerified.current) return;

    const statusParam = searchParams.get('status');
    const messageParam = searchParams.get('message');
    const code = searchParams.get('code');

    if (statusParam === 'success') {
      setStatus('success');
      setMessage('¡Tu cuenta ha sido verificada exitosamente!');
      hasVerified.current = true;
    } else if (statusParam === 'error') {
      setStatus('error');
      setMessage(messageParam || 'Error al verificar la cuenta');
      hasVerified.current = true;
    } else if (code && !hasVerified.current) {
      // Verificar directamente con el backend solo si no se ha verificado antes
      hasVerified.current = true; // Marcar como verificado antes de la llamada
      verifyAccount(code);
    } else {
      setStatus('error');
      setMessage('Enlace de verificación inválido');
      hasVerified.current = true;
    }
  }, [searchParams]);

  const verifyAccount = async (code: string) => {
    try {
      const response = await fetch(`http://localhost:9000/auth/verify?code=${code}`, {
        method: 'GET',
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStatus('success');
        setMessage('¡Tu cuenta ha sido verificada exitosamente!');
      } else {
        setStatus('error');
        setMessage(data.error || 'Error al verificar la cuenta');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Error de conexión. Intenta más tarde.');
    }
  };

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      textAlign: 'center'
    }}>
      {status === 'loading' && (
        <>
          <div style={{ marginBottom: '1rem' }}>Verificando cuenta...</div>
          <div>⏳</div>
        </>
      )}

      {status === 'success' && (
        <>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
          <h2 style={{ color: '#28a745', marginBottom: '1rem' }}>
            Verificación Exitosa
          </h2>
          <p style={{ marginBottom: '2rem' }}>{message}</p>
          <button
            onClick={handleGoHome}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Ir al Inicio
          </button>
        </>
      )}

      {status === 'error' && (
        <>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>
          <h2 style={{ color: '#dc3545', marginBottom: '1rem' }}>
            Error de Verificación
          </h2>
          <p style={{ marginBottom: '2rem' }}>{message}</p>
          <button
            onClick={handleGoHome}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Volver al Inicio
          </button>
        </>
      )}
    </div>
  );
};

export default EmailVerification;
