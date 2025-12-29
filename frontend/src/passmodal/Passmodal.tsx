import "./passmodal.css"

type Props = {
  open: boolean
  onClose: () => void
  message: string
}

export default function PasswordModal({ open, onClose, message }: Props) {
  if (!open) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <h2>Слабый пароль</h2>
        <p>{message}</p>

        <ul>
          <li>• минимум 8 символов</li>
          <li>• хотя бы одна буква</li>
          <li>• хотя бы одна цифра</li>
        </ul>

        <button onClick={onClose}>Понял</button>
      </div>
    </div>
  )
}