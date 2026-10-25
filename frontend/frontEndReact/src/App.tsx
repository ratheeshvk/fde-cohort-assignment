import { useState, useEffect } from 'react'
import Header from './components/Header'
import PatientRow from './components/PatientRow'
import Pagination from './components/Pagination'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
     <Header title="Patient Encounters" />
    </>
  )
}

export default App
