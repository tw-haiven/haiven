export default function Landing() {
  return (
    <div class="landing-page">
      <h3>Welcome to Haiven's "Guided mode"!</h3>
      <p>
        In this mode, you have a bit less flexibility than in the "Chat mode",
        but you gain some extra guidance and better visual display of the
        results.
      </p>
      <p>Let us know what you like better!</p>

      <div>
        <img
          className="sample-screenshot"
          src="/boba/screenshot_sample_guided_landing.png"
        />
      </div>
    </div>
  );
}
