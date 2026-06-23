module fir_filter (
	input  logic clk,
	input  logic rst_n,
	input  logic valid_in,
	input  logic signed [15:0] data_in,
	output logic valid_out,
	output logic signed [15:0] data_out
);

	localparam logic signed [15:0] COEFF0 = 16'sd4096;
	localparam logic signed [15:0] COEFF1 = 16'sd8192;
	localparam logic signed [15:0] COEFF2 = 16'sd8192;
	localparam logic signed [15:0] COEFF3 = 16'sd4096;
	localparam int SHIFT = 15;

	logic signed [15:0] x0;
	logic signed [15:0] x1;
	logic signed [15:0] x2;

	logic signed [39:0] p0_r;
	logic signed [39:0] p1_r;
	logic signed [39:0] p2_r;
	logic signed [39:0] p3_r;

	logic signed [39:0] s0_r;
	logic signed [39:0] s1_r;

	logic valid_s1;
	logic valid_s2;

	function automatic logic signed [15:0] saturate16(input logic signed [39:0] value);
		if (value > 40'sd32767) begin
			saturate16 = 16'sd32767;
		end else if (value < -40'sd32768) begin
			saturate16 = -16'sd32768;
		end else begin
			saturate16 = value[15:0];
		end
	endfunction

	always_ff @(posedge clk or negedge rst_n) begin
		if (!rst_n) begin
			x0 <= '0;
			x1 <= '0;
			x2 <= '0;
		end else if (valid_in) begin
			x0 <= data_in;
			x1 <= x0;
			x2 <= x1;
		end
	end

	always_ff @(posedge clk or negedge rst_n) begin
		if (!rst_n) begin
			p0_r <= '0;
			p1_r <= '0;
			p2_r <= '0;
			p3_r <= '0;
			valid_s1 <= 1'b0;
		end else begin
			valid_s1 <= valid_in;
			if (valid_in) begin
				p0_r <= data_in * COEFF0;
				p1_r <= x0 * COEFF1;
				p2_r <= x1 * COEFF2;
				p3_r <= x2 * COEFF3;
			end
		end
	end

	always_ff @(posedge clk or negedge rst_n) begin
		if (!rst_n) begin
			s0_r <= '0;
			s1_r <= '0;
			valid_s2 <= 1'b0;
		end else begin
			valid_s2 <= valid_s1;
			if (valid_s1) begin
				s0_r <= p0_r + p1_r;
				s1_r <= p2_r + p3_r;
			end
		end
	end

	always_ff @(posedge clk or negedge rst_n) begin
		if (!rst_n) begin
			data_out <= '0;
			valid_out <= 1'b0;
		end else begin
			valid_out <= valid_s2;
			if (valid_s2) begin
				data_out <= saturate16((s0_r + s1_r) >>> SHIFT);
			end
		end
	end

endmodule
