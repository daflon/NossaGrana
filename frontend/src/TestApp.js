import React from 'react';

function TestApp() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Teste Frontend</h1>
      <p>Se você está vendo isso, o React está funcionando!</p>
      <button onClick={() => alert('Botão funcionando!')}>
        Testar JavaScript
      </button>
    </div>
  );
}

export default TestApp;