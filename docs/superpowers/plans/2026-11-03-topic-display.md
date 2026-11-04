# Topic display implementation plan

Approved design: show distinct detected topics joined with ` + `, preserve sentiment and unspecified-topic label.

Implementation: retain existing topic code and add optional ordered `topics` for multiple topics. Update strict API/UI validation, rendering and asset versions. Verify real API and rendered labels for zero, one, two and three topics. Preserve detector/model artifacts.
