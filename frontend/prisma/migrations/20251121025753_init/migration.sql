-- CreateTable
CREATE TABLE "Stock" (
    "symbol" TEXT NOT NULL,
    "name" TEXT,
    "sector" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Stock_pkey" PRIMARY KEY ("symbol")
);

-- CreateTable
CREATE TABLE "Signal" (
    "id" SERIAL NOT NULL,
    "stockSymbol" TEXT NOT NULL,
    "price" DOUBLE PRECISION NOT NULL,
    "score" DOUBLE PRECISION NOT NULL,
    "status" TEXT NOT NULL,
    "rsi" DOUBLE PRECISION,
    "volatility" DOUBLE PRECISION,
    "aiAnalysis" TEXT,
    "analysisDate" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Signal_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Signal_analysisDate_idx" ON "Signal"("analysisDate");

-- CreateIndex
CREATE INDEX "Signal_stockSymbol_idx" ON "Signal"("stockSymbol");

-- AddForeignKey
ALTER TABLE "Signal" ADD CONSTRAINT "Signal_stockSymbol_fkey" FOREIGN KEY ("stockSymbol") REFERENCES "Stock"("symbol") ON DELETE CASCADE ON UPDATE CASCADE;
