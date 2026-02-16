import { io } from 'socket.io-client'

const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://127.0.0.1:5000'

export function createDashboardSocket({ onConnect, onDisconnect, onDashboardUpdate }) {
  const socket = io(socketUrl, {
    transports: ['websocket']
  })

  socket.on('connect', () => onConnect?.())
  socket.on('disconnect', () => onDisconnect?.())
  socket.on('update_dashboard', (payload) => onDashboardUpdate?.(payload))

  return socket
}
