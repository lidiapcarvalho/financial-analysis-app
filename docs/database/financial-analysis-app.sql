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
	"name" VARCHAR NOT NULL,
	"sector" VARCHAR NOT NULL,
	"currency" VARCHAR NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "financial_record" (
	"id" INTEGER NOT NULL,
	"company_id" INTEGER NOT NULL,
	"fiscal_year" INTEGER NOT NULL,
	"revenue" REAL NOT NULL,
	"operating_income" REAL NOT NULL,
	"net_income" REAL NOT NULL,
	"total_assets" REAL NOT NULL,
	"total_liabilities" REAL NOT NULL,
	"equity" REAL NOT NULL,
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
