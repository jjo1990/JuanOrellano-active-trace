import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusBadge } from '@/shared/components/StatusBadge'

describe('StatusBadge', () => {
  it('renders Atrasado with correct label', () => {
    render(<StatusBadge estado="Atrasado" />)
    expect(screen.getByText('Atrasado')).toBeInTheDocument()
  })

  it('renders Al día with correct label', () => {
    render(<StatusBadge estado="Al día" />)
    expect(screen.getByText('Al día')).toBeInTheDocument()
  })

  it('renders Pendiente with correct label', () => {
    render(<StatusBadge estado="Pendiente" />)
    expect(screen.getByText('Pendiente')).toBeInTheDocument()
  })

  it('renders Enviado with correct label', () => {
    render(<StatusBadge estado="Enviado" />)
    expect(screen.getByText('Enviado')).toBeInTheDocument()
  })

  it('renders Error with correct label', () => {
    render(<StatusBadge estado="Error" />)
    expect(screen.getByText('Error')).toBeInTheDocument()
  })

  it('renders Aprobado with correct label', () => {
    render(<StatusBadge estado="Aprobado" />)
    expect(screen.getByText('Aprobado')).toBeInTheDocument()
  })

  it('renders Desaprobado with correct label', () => {
    render(<StatusBadge estado="Desaprobado" />)
    expect(screen.getByText('Desaprobado')).toBeInTheDocument()
  })

  it('renders Cancelado with correct label', () => {
    render(<StatusBadge estado="Cancelado" />)
    expect(screen.getByText('Cancelado')).toBeInTheDocument()
  })

  it('renders Sin datos with correct label', () => {
    render(<StatusBadge estado="Sin datos" />)
    expect(screen.getByText('Sin datos')).toBeInTheDocument()
  })
})
