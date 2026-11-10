CREATE TABLE IF NOT EXISTS "user" (
	"id" INTEGER NOT NULL,
	"username" VARCHAR NOT NULL UNIQUE,
	"email" VARCHAR NOT NULL UNIQUE,
	"password_hash" VARCHAR NOT NULL,
	"created_at" TEXT NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "company" (
	"id" INTEGER NOT NULL,
	"name" VARCHAR NOT NULL UNIQUE,
	"sector" VARCHAR NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "financial_record" (
	"id" INTEGER NOT NULL,
	"company_id" INTEGER NOT NULL,
	"fiscal_year" INTEGER NOT NULL UNIQUE CHECK(>0),
	"period_end" TEXT NOT NULL,
	"currency" TEXT NOT NULL,
	"unit" TEXT NOT NULL,
	"revenue" REAL NOT NULL CHECK(>=0),
	"operating_income" REAL NOT NULL,
	"net_income" REAL NOT NULL,
	"total_assets" REAL NOT NULL CHECK(>=0),
	"total_liabilities" REAL NOT NULL CHECK(>=0),
	"equity" REAL NOT NULL,
	"equity_attributable_to_owners" REAL NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY ("company_id") REFERENCES "company"("id")
	ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "financial_record_unique_0" UNIQUE ("company_id", "fiscal_year")
);

CREATE TABLE IF NOT EXISTS "saved_comparison" (
	"id" INTEGER NOT NULL,
	"user_id" INTEGER NOT NULL,
	"name" VARCHAR NOT NULL,
	"created_at" TEXT NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY ("user_id") REFERENCES "user"("id")
	ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS "comparison_company" (
	"comparison_id" INTEGER NOT NULL,
	"company_id" INTEGER NOT NULL,
	PRIMARY KEY("comparison_id", "company_id"),
	FOREIGN KEY ("comparison_id") REFERENCES "saved_comparison"("id")
	ON UPDATE NO ACTION ON DELETE NO ACTION,
	FOREIGN KEY ("company_id") REFERENCES "company"("id")
	ON UPDATE NO ACTION ON DELETE NO ACTION
);
