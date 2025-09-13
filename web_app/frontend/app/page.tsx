export default function Home() {
  return (
    <main>
      <h1>Under construction. Select one URL in the list below to test:</h1>
      <ul style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <li>
          <a href="http://localhost:8001/admin/">Admin Page (Django)</a>
        </li>
        <li>
          <a href="http://localhost:8001/api/">API View and Testing - Restful API of Django</a>
        </li>
        <li>
          <a href="http://localhost:8001/api/schema/swagger-ui/">API Documentation and Testing - Swagger UI</a>
        </li>
        <li>
          <a href="http://localhost:8001/api/schema/redoc/">API Documentation and Testing - ReDoc</a>
        </li>
        <li>
          <a href="http://localhost:8001/api/schema/"> Download Schema.Yaml of API</a>
        </li>
        <li>
          <a href="http://localhost:8000/chatbot">Chat Bot (Under construction - No connection)</a>
        </li>
      </ul>
    </main>
  )
}
