import Ajv from "ajv";
import handSchema from "../schemas/hand.schema.json";

const ajv = new Ajv({ allErrors: true });
const validate = ajv.compile(handSchema);

export function validateHandMinimal(obj: unknown): boolean {
  const ok = validate(obj);
  if (!ok) {
    // console.debug(validate.errors);
  }
  return !!ok;
}
