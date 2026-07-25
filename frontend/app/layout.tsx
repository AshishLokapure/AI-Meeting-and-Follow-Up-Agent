export const metadata = {
  title: 'AI Meeting Agent',
  description: 'AI-powered meeting and follow-up assistant',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
