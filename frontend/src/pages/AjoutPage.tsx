import { TextField, FileField, CheckboxField, NumberField, DateField } from '../components/form'

function AjoutPage() {
  return (
    <div>
      <h2>Ajout</h2>
      <form>
        <TextField label="Nom" placeholder="Nom de la gamme" required />
        <NumberField label="Quantité" min={0} step={1} />
        <DateField label="Date" />
        <FileField label="Fichier" accept="image/*" />
        <CheckboxField label="Actif" defaultChecked />
      </form>
    </div>
  )
}

export default AjoutPage
