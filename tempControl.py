from shapely import Polygon, union_all, centroid

class TriangularMembershipFunction:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def membership(self, x):
        if x < self.a:
            return 0
        elif x <= self.b and self.a != self.b:
            return (x - self.a) / (self.b - self.a)
        elif x <= self.c:
            return (self.c - x) / (self.c - self.b)
        else:
            return 0

    def cutBy(self, upperLimit):
        return [
            (self.a, 0),
            (self.a + upperLimit * (self.b - self.a), upperLimit),
            (self.c - upperLimit * (self.c - self.b), upperLimit),
            (self.c, 0),
        ]

class FuzzyVariable:
    def __init__(self, values, membershipFns):
        self.values = values
        self.membershipFns = membershipFns

    def membership(self, x):
        return {elem: membershipFn.membership(x) for (elem, membershipFn) in zip(self.values, self.membershipFns)}
    
    def getMembershipFn(self, value):
        return self.membershipFns[self.values.index(value)]

class FuzzyRule:
    def __init__(self, name, lhs, rhs, ruleStrength):
        self.name = name
        self.lhs = lhs
        self.rhs = rhs
        self.ruleStrength = ruleStrength

    def evaluate(self, fuzzyInput):
        lhsValue = fuzzyInput.get(self.lhs, 0)
        rhsValue = min(lhsValue, self.ruleStrength)
        print(f"Rule {self.name}: degree of activation = {rhsValue}")
        return self.rhs, rhsValue

class TemperatureController:
    def __init__(self, temperature, heaterPower, fuzzyRules):
        self.temperature = temperature
        self.heaterPower = heaterPower
        self.fuzzyRules = fuzzyRules

    def inference(self, inputTemp):
        fuzzyInput = self.fuzzifyInput(inputTemp)
        print("Fuzzyfied Inputs:", fuzzyInput)

        fuzzyOutputDistribution = self.fuzzyInference(fuzzyInput, self.heaterPower, self.fuzzyRules)
        print("Aggregated Fuzzy Output Distribution:", fuzzyOutputDistribution)

        outputPower = self.defuzzifyOutput(fuzzyOutputDistribution)
        return outputPower

    def fuzzifyInput(self, inputTemp):
        return self.temperature.membership(inputTemp)

    def fuzzyInference(self, fuzzyInput, fuzzyOutputVar, fuzzyRules):
        fuzzyOutputs = {}
        for rule in fuzzyRules:
            rhs, rhsValue = rule.evaluate(fuzzyInput)
            fuzzyOutputs[rhs] = rhsValue
        
        polygon = None

        for fuzzyVar in fuzzyOutputs:
            polygonVertices = fuzzyOutputVar.getMembershipFn(fuzzyVar).cutBy(fuzzyOutputs[fuzzyVar])
            polygon = union_all([polygon, Polygon(polygonVertices + [polygonVertices[0]])])

        return polygon

    def defuzzifyOutput(self, fuzzyOutputDistribution):
        print(fuzzyOutputDistribution, type(fuzzyOutputDistribution))
        return centroid(fuzzyOutputDistribution).x

temperature = FuzzyVariable(["Cold", "Warm", "Hot"], [
    TriangularMembershipFunction(10, 10, 20),
    TriangularMembershipFunction(20, 25, 30),
    TriangularMembershipFunction(30, 40, 40)
])

heaterPower = FuzzyVariable(["Low", "Medium", "High"], [
    TriangularMembershipFunction(0, 0, 30),
    TriangularMembershipFunction(40, 50, 60),
    TriangularMembershipFunction(60, 100, 100)
])

fuzzyRules = [
    FuzzyRule("R1", "Cold", "High", 1),
    FuzzyRule("R2", "Warm", "Medium", 1),
    FuzzyRule("R3", "Hot", "Low", 1),
]

controller = TemperatureController(temperature, heaterPower, fuzzyRules)

input_temp = 28
print("Input Temperature: ", input_temp)
finalHeaterPower = controller.inference(input_temp)
print("Output Heater Power: ", finalHeaterPower)
print()

input_temp = 40
print("Input Temperature: ", input_temp)
finalHeaterPower = controller.inference(input_temp)
print("Output Heater Power: ", finalHeaterPower)
print()

input_temp = 10
print("Input Temperature: ", input_temp)
finalHeaterPower = controller.inference(input_temp)
print("Output Heater Power: ", finalHeaterPower)
