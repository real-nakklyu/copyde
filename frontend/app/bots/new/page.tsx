import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { CopySettingsForm } from "@/components/CopySettingsForm"
import { TradingCard } from "@/components/TradingCard"

export default function NewBotPage({ searchParams }: { searchParams: { leader?: string } }) {
  return (
    <BinanceStyleLayout>
      <TradingCard title="Create Copy Bot">
        <CopySettingsForm leaderId={searchParams.leader} />
      </TradingCard>
    </BinanceStyleLayout>
  )
}

