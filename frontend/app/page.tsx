import PlayField from "../components/PlayField";
import HandHistory from "../components/HandHistory";

export default function Home() {
  return (
    <main style={{display: 'flex', gap: 20, padding: 20}}>
      <div style={{flex: 1}}>
        <h2>Playing Field Log</h2>
        <PlayField />
      </div>
      <div style={{flex: 1}}>
        <h2>Hand History</h2>
        <HandHistory />
      </div>
    </main>
  );
}
